from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Query
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import secrets
import io
import csv
import json
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt as pyjwt
import razorpay
import hashlib
import hmac

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="VitalTrack API")
api_router = APIRouter(prefix="/api")

JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')
JWT_ALGORITHM = "HS256"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== CONSTANTS ====================
VITAL_TYPES = [
    {"key": "blood_glucose", "name": "Blood Glucose", "unit": "mg/dL", "min": 20, "max": 600, "normal_min": 70, "normal_max": 140, "chart_type": "line", "category": "metabolic"},
    {"key": "blood_oxygen", "name": "Blood Oxygen", "unit": "%", "min": 70, "max": 100, "normal_min": 95, "normal_max": 100, "chart_type": "area", "category": "respiratory"},
    {"key": "blood_pressure", "name": "Blood Pressure", "unit": "mmHg", "min": 60, "max": 250, "normal_min": 90, "normal_max": 140, "chart_type": "dual_line", "category": "cardiovascular", "has_dual_value": True, "value2_label": "Diastolic", "value2_min": 40, "value2_max": 150, "value2_normal_min": 60, "value2_normal_max": 90},
    {"key": "bmi", "name": "BMI", "unit": "kg/m2", "min": 10, "max": 60, "normal_min": 18.5, "normal_max": 24.9, "chart_type": "line", "category": "body"},
    {"key": "body_temperature", "name": "Body Temperature", "unit": "F", "min": 90, "max": 110, "normal_min": 97, "normal_max": 99.5, "chart_type": "line", "category": "general"},
    {"key": "heart_rate", "name": "Heart Rate", "unit": "bpm", "min": 30, "max": 250, "normal_min": 60, "normal_max": 100, "chart_type": "line", "category": "cardiovascular"},
    {"key": "respiratory_rate", "name": "Respiratory Rate", "unit": "breaths/min", "min": 5, "max": 60, "normal_min": 12, "normal_max": 20, "chart_type": "line", "category": "respiratory"},
    {"key": "sleep_duration", "name": "Sleep Duration", "unit": "hours", "min": 0, "max": 24, "normal_min": 7, "normal_max": 9, "chart_type": "bar", "category": "lifestyle"},
    {"key": "physical_activity", "name": "Physical Activity", "unit": "minutes", "min": 0, "max": 1440, "normal_min": 30, "normal_max": 120, "chart_type": "bar", "category": "lifestyle"},
    {"key": "waist_circumference", "name": "Waist Circumference", "unit": "cm", "min": 40, "max": 200, "normal_min": 60, "normal_max": 102, "chart_type": "line", "category": "body"},
    {"key": "weight", "name": "Weight", "unit": "kg", "min": 20, "max": 300, "normal_min": 50, "normal_max": 100, "chart_type": "line", "category": "body"},
    {"key": "hydration", "name": "Hydration Level", "unit": "glasses", "min": 0, "max": 30, "normal_min": 8, "normal_max": 15, "chart_type": "bar", "category": "lifestyle"},
]

PLANS = [
    {"key": "free", "name": "Free", "price": 0, "price_yearly": 0, "currency": "INR", "vital_limit": 2, "chart_history_days": 7, "csv_export": True, "pdf_export": False, "sharing": False, "features": ["Track any 2 vitals", "7-day chart history", "Basic CSV export", "Basic reminders"]},
    {"key": "standard", "name": "Standard", "price": 299, "price_yearly": 2999, "currency": "INR", "vital_limit": 6, "chart_history_days": 365, "csv_export": True, "pdf_export": True, "sharing": True, "features": ["Track any 6 vitals", "Full 1-year history", "CSV & PDF export", "Shareable reports", "Advanced reminders", "Better analytics"]},
    {"key": "premium", "name": "Premium", "price": 499, "price_yearly": 4999, "currency": "INR", "vital_limit": 12, "chart_history_days": -1, "csv_export": True, "pdf_export": True, "sharing": True, "features": ["Track all 12 vitals", "Unlimited history", "All export formats", "Full sharing", "Priority support", "Advanced analytics"]},
]

VITAL_KEYS = [v["key"] for v in VITAL_TYPES]

# Razorpay client
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
razorpay_client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    logger.info("Razorpay client initialized")

# Translations
TRANSLATIONS = {
    "en": {
        "app_name": "VitalTrack", "dashboard": "Dashboard", "daily_tracker": "Daily Tracker",
        "charts_trends": "Charts & Trends", "reports": "Reports", "billing": "Billing",
        "settings": "Settings", "admin_panel": "Admin Panel", "sign_out": "Sign Out",
        "welcome_back": "Welcome back", "active_vitals": "Active Vitals", "todays_entries": "Today's Entries",
        "this_week": "This Week", "plan": "Plan", "health_insights": "Health Insights",
        "quick_actions": "Quick Actions", "your_vitals": "Your Vitals", "log_todays_vitals": "Log Today's Vitals",
        "view_trends": "View Trends", "export_report": "Export Report", "enable_vitals": "Enable Vitals",
        "get_started": "Get Started", "save_all": "Save All", "no_vitals_enabled": "No Vitals Enabled",
        "select_vital": "Select vital", "date_range": "Date Range", "export": "Export",
        "current_plan": "Current Plan", "upgrade": "Upgrade", "downgrade": "Downgrade",
        "switch": "Switch", "profile": "Profile", "manage_vitals": "Manage Vitals",
        "save_profile": "Save Profile", "full_name": "Full Name", "email": "Email",
        "password": "Password", "sign_in": "Sign In", "create_account": "Create Account",
        "dont_have_account": "Don't have an account?", "already_have_account": "Already have an account?",
        "dark_mode": "Dark Mode", "language": "Language", "subscription_billing": "Subscription & Billing",
        "reports_export": "Reports & Export", "shared_reports": "Shared Reports",
        "create_shared_report": "Create Shared Report", "share_link": "Share Link",
        "password_protected": "Password Protected", "expires_in": "Expires in",
        "revoke": "Revoke", "copy_link": "Copy Link", "normal": "Normal", "warning": "Warning",
        "critical": "Critical", "medical_disclaimer": "For informational tracking only. Not a medical device.",
    },
    "hi": {
        "app_name": "VitalTrack", "dashboard": "डैशबोर्ड", "daily_tracker": "दैनिक ट्रैकर",
        "charts_trends": "चार्ट और रुझान", "reports": "रिपोर्ट", "billing": "बिलिंग",
        "settings": "सेटिंग्स", "admin_panel": "एडमिन पैनल", "sign_out": "साइन आउट",
        "welcome_back": "वापस स्वागत है", "active_vitals": "सक्रिय वाइटल्स", "todays_entries": "आज की एंट्री",
        "this_week": "इस सप्ताह", "plan": "प्लान", "health_insights": "स्वास्थ्य अंतर्दृष्टि",
        "quick_actions": "त्वरित कार्य", "your_vitals": "आपके वाइटल्स", "log_todays_vitals": "आज के वाइटल्स दर्ज करें",
        "view_trends": "रुझान देखें", "export_report": "रिपोर्ट निर्यात करें", "enable_vitals": "वाइटल्स सक्षम करें",
        "get_started": "शुरू करें", "save_all": "सब सेव करें", "no_vitals_enabled": "कोई वाइटल्स सक्षम नहीं",
        "select_vital": "वाइटल चुनें", "date_range": "तारीख सीमा", "export": "निर्यात",
        "current_plan": "वर्तमान प्लान", "upgrade": "अपग्रेड", "downgrade": "डाउनग्रेड",
        "switch": "बदलें", "profile": "प्रोफ़ाइल", "manage_vitals": "वाइटल्स प्रबंधित करें",
        "save_profile": "प्रोफ़ाइल सेव करें", "full_name": "पूरा नाम", "email": "ईमेल",
        "password": "पासवर्ड", "sign_in": "साइन इन", "create_account": "खाता बनाएं",
        "dont_have_account": "खाता नहीं है?", "already_have_account": "पहले से खाता है?",
        "dark_mode": "डार्क मोड", "language": "भाषा", "subscription_billing": "सदस्यता और बिलिंग",
        "reports_export": "रिपोर्ट और निर्यात", "shared_reports": "साझा रिपोर्ट",
        "create_shared_report": "साझा रिपोर्ट बनाएं", "share_link": "लिंक साझा करें",
        "password_protected": "पासवर्ड संरक्षित", "expires_in": "समाप्ति",
        "revoke": "रद्द करें", "copy_link": "लिंक कॉपी करें", "normal": "सामान्य", "warning": "चेतावनी",
        "critical": "गंभीर", "medical_disclaimer": "केवल सूचना ट्रैकिंग के लिए। चिकित्सा उपकरण नहीं है।",
    },
    "te": {
        "app_name": "VitalTrack", "dashboard": "డాష్‌బోర్డ్", "daily_tracker": "దైనిక ట్రాకర్",
        "charts_trends": "చార్ట్‌లు & ట్రెండ్‌లు", "reports": "రిపోర్ట్‌లు", "billing": "బిల్లింగ్",
        "settings": "సెట్టింగ్‌లు", "admin_panel": "అడ్మిన్ ప్యానెల్", "sign_out": "సైన్ అవుట్",
        "welcome_back": "తిరిగి స్వాగతం", "active_vitals": "యాక్టివ్ వైటల్స్", "todays_entries": "ఈరోజు ఎంట్రీలు",
        "this_week": "ఈ వారం", "plan": "ప్లాన్", "health_insights": "ఆరోగ్య అంతర్దృష్టులు",
        "quick_actions": "త్వరిత చర్యలు", "your_vitals": "మీ వైటల్స్", "log_todays_vitals": "ఈరోజు వైటల్స్ నమోదు చేయండి",
        "view_trends": "ట్రెండ్‌లు చూడండి", "export_report": "రిపోర్ట్ ఎగుమతి చేయండి", "enable_vitals": "వైటల్స్ ఎనేబుల్ చేయండి",
        "get_started": "ప్రారంభించండి", "save_all": "అన్నీ సేవ్ చేయండి", "no_vitals_enabled": "వైటల్స్ ఎనేబుల్ కాలేదు",
        "select_vital": "వైటల్ ఎంచుకోండి", "date_range": "తేదీ పరిధి", "export": "ఎగుమతి",
        "current_plan": "ప్రస్తుత ప్లాన్", "upgrade": "అప్‌గ్రేడ్", "downgrade": "డౌన్‌గ్రేడ్",
        "switch": "మార్చు", "profile": "ప్రొఫైల్", "manage_vitals": "వైటల్స్ నిర్వహించండి",
        "save_profile": "ప్రొఫైల్ సేవ్ చేయండి", "full_name": "పూర్తి పేరు", "email": "ఇమెయిల్",
        "password": "పాస్‌వర్డ్", "sign_in": "సైన్ ఇన్", "create_account": "ఖాతా సృష్టించండి",
        "dont_have_account": "ఖాతా లేదా?", "already_have_account": "ఇప్పటికే ఖాతా ఉందా?",
        "dark_mode": "డార్క్ మోడ్", "language": "భాష", "subscription_billing": "సబ్‌స్క్రిప్షన్ & బిల్లింగ్",
        "reports_export": "రిపోర్ట్‌లు & ఎగుమతి", "shared_reports": "షేర్డ్ రిపోర్ట్‌లు",
        "create_shared_report": "షేర్డ్ రిపోర్ట్ సృష్టించండి", "share_link": "లింక్ షేర్ చేయండి",
        "password_protected": "పాస్‌వర్డ్ రక్షిత", "expires_in": "గడువు",
        "revoke": "రద్దు", "copy_link": "లింక్ కాపీ చేయండి", "normal": "సాధారణ", "warning": "హెచ్చరిక",
        "critical": "తీవ్ర", "medical_disclaimer": "సమాచార ట్రాకింగ్ కోసం మాత్రమే. వైద్య పరికరం కాదు.",
    },
}

# ==================== PYDANTIC MODELS ====================
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class EntryData(BaseModel):
    vital_key: str
    date: str
    value: float
    value2: Optional[float] = None
    notes: Optional[str] = None

class BulkEntryRequest(BaseModel):
    entries: List[EntryData]

class ReminderRequest(BaseModel):
    vital_keys: List[str] = []
    time: str = "08:00"
    frequency: str = "daily"
    enabled: bool = True

class ExportRequest(BaseModel):
    vital_keys: List[str]
    start_date: str
    end_date: str
    format: str = "csv"

class SharedReportRequest(BaseModel):
    vital_keys: List[str]
    start_date: str
    end_date: str
    expires_days: int = 7
    password: Optional[str] = None

class SharedReportAccessRequest(BaseModel):
    password: Optional[str] = None

class RazorpayOrderRequest(BaseModel):
    plan_key: str
    billing_cycle: str = "monthly"

class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan_key: str

class VitalToggleRequest(BaseModel):
    vital_key: str
    enabled: bool

class PlanChangeRequest(BaseModel):
    plan_key: str

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

# ==================== AUTH UTILITIES ====================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(hours=1), "type": "access"}
    return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}
    return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def set_auth_cookies(response: Response, access: str, refresh: str):
    response.set_cookie("access_token", access, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
    response.set_cookie("refresh_token", refresh, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")

def serialize_user(user: dict) -> dict:
    u = {k: v for k, v in user.items() if k != "_id" and k != "password_hash"}
    u["id"] = str(user["_id"])
    if "created_at" in u and isinstance(u["created_at"], datetime):
        u["created_at"] = u["created_at"].isoformat()
    if "updated_at" in u and isinstance(u["updated_at"], datetime):
        u["updated_at"] = u["updated_at"].isoformat()
    return u

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_admin_user(request: Request) -> dict:
    user = await get_current_user(request)
    if user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def get_user_plan(user: dict) -> dict:
    plan_key = user.get("plan", "free")
    for p in PLANS:
        if p["key"] == plan_key:
            return p
    return PLANS[0]

# ==================== STARTUP ====================
@app.on_event("startup")
async def startup():
    logger.info("Starting VitalTrack API...")
    # Indexes
    await db.users.create_index("email", unique=True)
    await db.daily_entries.create_index([("user_id", 1), ("vital_key", 1), ("date", 1)], unique=True)
    await db.daily_entries.create_index([("user_id", 1), ("date", 1)])
    await db.reminders.create_index("user_id")
    await db.exports.create_index("user_id")
    await db.shared_reports.create_index("token", unique=True)
    await db.login_attempts.create_index("identifier")
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.audit_logs.create_index([("user_id", 1), ("created_at", -1)])
    # Seed vital types
    for vt in VITAL_TYPES:
        await db.vital_types.update_one({"key": vt["key"]}, {"$set": vt}, upsert=True)
    # Seed plans
    for p in PLANS:
        await db.plans.update_one({"key": p["key"]}, {"$set": p}, upsert=True)
    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({
            "email": admin_email, "password_hash": hash_password(admin_password),
            "name": "Admin", "role": "super_admin", "plan": "premium",
            "enabled_vitals": VITAL_KEYS, "settings": {"language": "en"},
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)
        })
        logger.info(f"Admin user created: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})
    # Write test credentials
    creds_dir = Path("/app/memory")
    creds_dir.mkdir(exist_ok=True)
    with open(creds_dir / "test_credentials.md", "w") as f:
        f.write(f"# Test Credentials\n\n## Admin\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: super_admin\n\n## Test User\n- Register at /register with any email\n\n## Endpoints\n- Login: POST /api/auth/login\n- Register: POST /api/auth/register\n- Me: GET /api/auth/me\n")
    logger.info("VitalTrack API started successfully")

@app.on_event("shutdown")
async def shutdown():
    client.close()

# ==================== AUTH ROUTES ====================
@api_router.post("/auth/register")
async def register(req: RegisterRequest, response: Response):
    email = req.email.lower().strip()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    user_doc = {
        "email": email, "password_hash": hash_password(req.password),
        "name": req.name.strip(), "role": "user", "plan": "free",
        "enabled_vitals": [], "settings": {"language": "en"},
        "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    access = create_access_token(str(result.inserted_id), email)
    refresh = create_refresh_token(str(result.inserted_id))
    set_auth_cookies(response, access, refresh)
    await db.audit_logs.insert_one({"user_id": str(result.inserted_id), "action": "register", "created_at": datetime.now(timezone.utc)})
    return serialize_user(user_doc)

@api_router.post("/auth/login")
async def login(req: LoginRequest, request: Request, response: Response):
    email = req.email.lower().strip()
    ip = request.client.host if request.client else "unknown"
    identifier = f"{ip}:{email}"
    # Brute force check
    attempts = await db.login_attempts.find_one({"identifier": identifier})
    if attempts and attempts.get("count", 0) >= 5:
        last = attempts.get("last_attempt", datetime.now(timezone.utc))
        if isinstance(last, str):
            last = datetime.fromisoformat(last)
        if datetime.now(timezone.utc) - last < timedelta(minutes=15):
            raise HTTPException(status_code=429, detail="Too many login attempts. Try again in 15 minutes.")
        else:
            await db.login_attempts.delete_one({"identifier": identifier})
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(req.password, user["password_hash"]):
        await db.login_attempts.update_one(
            {"identifier": identifier},
            {"$inc": {"count": 1}, "$set": {"last_attempt": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")
    await db.login_attempts.delete_one({"identifier": identifier})
    access = create_access_token(str(user["_id"]), email)
    refresh = create_refresh_token(str(user["_id"]))
    set_auth_cookies(response, access, refresh)
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}})
    await db.audit_logs.insert_one({"user_id": str(user["_id"]), "action": "login", "created_at": datetime.now(timezone.utc)})
    return serialize_user(user)

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return serialize_user(user)

@api_router.post("/auth/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        access = create_access_token(str(user["_id"]), user["email"])
        response.set_cookie("access_token", access, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
        return serialize_user(user)
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@api_router.post("/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    user = await db.users.find_one({"email": req.email.lower().strip()})
    if user:
        token = secrets.token_urlsafe(32)
        await db.password_reset_tokens.insert_one({
            "token": token, "user_id": str(user["_id"]),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "used": False
        })
        logger.info(f"Password reset token for {req.email}: {token}")
    return {"message": "If the email exists, a reset link has been sent"}

@api_router.post("/auth/reset-password")
async def reset_password(req: ResetPasswordRequest):
    record = await db.password_reset_tokens.find_one({"token": req.token, "used": False})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    if isinstance(record["expires_at"], str):
        expires = datetime.fromisoformat(record["expires_at"])
    else:
        expires = record["expires_at"]
    if datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=400, detail="Token expired")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    await db.users.update_one({"_id": ObjectId(record["user_id"])}, {"$set": {"password_hash": hash_password(req.password)}})
    await db.password_reset_tokens.update_one({"token": req.token}, {"$set": {"used": True}})
    return {"message": "Password reset successfully"}

# ==================== PROFILE ROUTES ====================
@api_router.put("/profile")
async def update_profile(req: ProfileUpdateRequest, request: Request):
    user = await get_current_user(request)
    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if req.name:
        updates["name"] = req.name.strip()
    if req.settings:
        current = user.get("settings", {})
        current.update(req.settings)
        updates["settings"] = current
    await db.users.update_one({"_id": user["_id"]}, {"$set": updates})
    updated = await db.users.find_one({"_id": user["_id"]})
    return serialize_user(updated)

# ==================== VITAL ROUTES ====================
@api_router.get("/vitals/types")
async def get_vital_types():
    return VITAL_TYPES

@api_router.get("/vitals/enabled")
async def get_enabled_vitals(request: Request):
    user = await get_current_user(request)
    enabled = user.get("enabled_vitals", [])
    return {"enabled_vitals": enabled, "plan": user.get("plan", "free"), "vital_limit": get_user_plan(user)["vital_limit"]}

@api_router.post("/vitals/toggle")
async def toggle_vital(req: VitalToggleRequest, request: Request):
    user = await get_current_user(request)
    if req.vital_key not in VITAL_KEYS:
        raise HTTPException(status_code=400, detail="Invalid vital key")
    enabled = user.get("enabled_vitals", [])
    plan = get_user_plan(user)
    if req.enabled:
        if req.vital_key in enabled:
            return {"enabled_vitals": enabled, "message": "Already enabled"}
        if len(enabled) >= plan["vital_limit"]:
            raise HTTPException(status_code=403, detail=f"Your {plan['name']} plan allows only {plan['vital_limit']} vitals. Upgrade to track more.")
        enabled.append(req.vital_key)
    else:
        enabled = [v for v in enabled if v != req.vital_key]
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"enabled_vitals": enabled, "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"enabled_vitals": enabled, "message": f"Vital {'enabled' if req.enabled else 'disabled'}"}

# ==================== ENTRY ROUTES ====================
@api_router.get("/entries")
async def get_entries(request: Request, start_date: str = Query(...), end_date: str = Query(...)):
    user = await get_current_user(request)
    uid = str(user["_id"])
    entries = await db.daily_entries.find(
        {"user_id": uid, "date": {"$gte": start_date, "$lte": end_date}},
        {"_id": 0}
    ).to_list(5000)
    return entries

@api_router.post("/entries")
async def save_entry(entry: EntryData, request: Request):
    user = await get_current_user(request)
    uid = str(user["_id"])
    if entry.vital_key not in user.get("enabled_vitals", []):
        raise HTTPException(status_code=403, detail="This vital is not enabled for your account")
    vtype = next((v for v in VITAL_TYPES if v["key"] == entry.vital_key), None)
    if vtype and (entry.value < vtype["min"] or entry.value > vtype["max"]):
        raise HTTPException(status_code=400, detail=f"Value must be between {vtype['min']} and {vtype['max']}")
    doc = {"user_id": uid, "vital_key": entry.vital_key, "date": entry.date,
           "value": entry.value, "value2": entry.value2, "notes": entry.notes,
           "updated_at": datetime.now(timezone.utc).isoformat()}
    await db.daily_entries.update_one(
        {"user_id": uid, "vital_key": entry.vital_key, "date": entry.date},
        {"$set": doc, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Entry saved", "entry": {k: v for k, v in doc.items() if k != "_id"}}

@api_router.post("/entries/bulk")
async def save_bulk_entries(req: BulkEntryRequest, request: Request):
    user = await get_current_user(request)
    uid = str(user["_id"])
    enabled = user.get("enabled_vitals", [])
    saved = 0
    errors = []
    for entry in req.entries:
        if entry.vital_key not in enabled:
            errors.append(f"{entry.vital_key}: not enabled")
            continue
        doc = {"user_id": uid, "vital_key": entry.vital_key, "date": entry.date,
               "value": entry.value, "value2": entry.value2, "notes": entry.notes,
               "updated_at": datetime.now(timezone.utc).isoformat()}
        await db.daily_entries.update_one(
            {"user_id": uid, "vital_key": entry.vital_key, "date": entry.date},
            {"$set": doc, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
        saved += 1
    return {"saved": saved, "errors": errors}

@api_router.delete("/entries/{date}/{vital_key}")
async def delete_entry(date: str, vital_key: str, request: Request):
    user = await get_current_user(request)
    result = await db.daily_entries.delete_one({"user_id": str(user["_id"]), "date": date, "vital_key": vital_key})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted"}

# ==================== CHART ROUTES ====================
@api_router.get("/charts/{vital_key}")
async def get_chart_data(vital_key: str, request: Request, start_date: str = Query(...), end_date: str = Query(...)):
    user = await get_current_user(request)
    plan = get_user_plan(user)
    if plan["chart_history_days"] > 0:
        earliest = (datetime.now(timezone.utc) - timedelta(days=plan["chart_history_days"])).strftime("%Y-%m-%d")
        if start_date < earliest:
            start_date = earliest
    entries = await db.daily_entries.find(
        {"user_id": str(user["_id"]), "vital_key": vital_key, "date": {"$gte": start_date, "$lte": end_date}},
        {"_id": 0}
    ).sort("date", 1).to_list(1000)
    vtype = next((v for v in VITAL_TYPES if v["key"] == vital_key), None)
    values = [e["value"] for e in entries if e.get("value") is not None]
    stats = {}
    if values:
        stats = {"min": min(values), "max": max(values), "avg": round(sum(values) / len(values), 1), "count": len(values)}
    return {"entries": entries, "vital_type": vtype, "stats": stats, "start_date": start_date, "end_date": end_date}

# ==================== INSIGHTS ROUTES ====================
@api_router.get("/insights")
async def get_insights(request: Request):
    user = await get_current_user(request)
    uid = str(user["_id"])
    enabled = user.get("enabled_vitals", [])
    insights = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    two_weeks_ago = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%d")

    for vk in enabled:
        vtype = next((v for v in VITAL_TYPES if v["key"] == vk), None)
        if not vtype:
            continue
        recent = await db.daily_entries.find(
            {"user_id": uid, "vital_key": vk, "date": {"$gte": week_ago, "$lte": today}},
            {"_id": 0}
        ).sort("date", 1).to_list(100)
        values = [e["value"] for e in recent if e.get("value") is not None]
        if not values:
            insights.append({"vital_key": vk, "type": "warning", "message": f"No {vtype['name']} entries this week. Start tracking!"})
            continue
        avg = sum(values) / len(values)
        missed = 7 - len(values)
        if missed >= 3:
            insights.append({"vital_key": vk, "type": "info", "message": f"{missed} missed {vtype['name']} entries this week"})
        if avg < vtype["normal_min"]:
            insights.append({"vital_key": vk, "type": "warning", "message": f"Your average {vtype['name']} ({round(avg,1)} {vtype['unit']}) is below normal range"})
        elif avg > vtype["normal_max"]:
            insights.append({"vital_key": vk, "type": "warning", "message": f"Your average {vtype['name']} ({round(avg,1)} {vtype['unit']}) is above normal range"})
        else:
            insights.append({"vital_key": vk, "type": "success", "message": f"Your {vtype['name']} is within normal range"})
        # Trend analysis
        prev_week = await db.daily_entries.find(
            {"user_id": uid, "vital_key": vk, "date": {"$gte": two_weeks_ago, "$lt": week_ago}},
            {"_id": 0}
        ).to_list(100)
        prev_values = [e["value"] for e in prev_week if e.get("value") is not None]
        if prev_values and values:
            prev_avg = sum(prev_values) / len(prev_values)
            change = ((avg - prev_avg) / prev_avg) * 100 if prev_avg else 0
            if abs(change) > 5:
                direction = "increased" if change > 0 else "decreased"
                insights.append({"vital_key": vk, "type": "info", "message": f"{vtype['name']} has {direction} by {abs(round(change,1))}% compared to last week"})
    return {"insights": insights}

# ==================== PLAN ROUTES ====================
@api_router.get("/plans")
async def get_plans():
    return PLANS

@api_router.get("/subscription")
async def get_subscription(request: Request):
    user = await get_current_user(request)
    plan = get_user_plan(user)
    sub = await db.subscriptions.find_one({"user_id": str(user["_id"]), "status": "active"}, {"_id": 0})
    return {"plan": plan, "subscription": sub, "enabled_vitals": user.get("enabled_vitals", []), "vital_limit": plan["vital_limit"]}

@api_router.post("/subscription/change")
async def change_subscription(req: PlanChangeRequest, request: Request):
    user = await get_current_user(request)
    uid = str(user["_id"])
    new_plan = next((p for p in PLANS if p["key"] == req.plan_key), None)
    if not new_plan:
        raise HTTPException(status_code=400, detail="Invalid plan")
    old_plan = get_user_plan(user)
    enabled = user.get("enabled_vitals", [])
    # On downgrade, truncate enabled vitals
    if new_plan["vital_limit"] < len(enabled):
        enabled = enabled[:new_plan["vital_limit"]]
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"plan": req.plan_key, "enabled_vitals": enabled, "updated_at": datetime.now(timezone.utc).isoformat()}})
    # Create subscription record
    await db.subscriptions.update_one(
        {"user_id": uid, "status": "active"},
        {"$set": {"plan_key": req.plan_key, "status": "active", "started_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    await db.audit_logs.insert_one({"user_id": uid, "action": "plan_change", "details": f"{old_plan['key']} -> {req.plan_key}", "created_at": datetime.now(timezone.utc)})
    return {"message": f"Plan changed to {new_plan['name']}", "plan": new_plan, "enabled_vitals": enabled}

# ==================== EXPORT ROUTES ====================
@api_router.post("/exports/generate")
async def generate_export(req: ExportRequest, request: Request):
    user = await get_current_user(request)
    plan = get_user_plan(user)
    if req.format == "pdf" and not plan["pdf_export"]:
        raise HTTPException(status_code=403, detail="PDF export requires Standard or Premium plan")
    uid = str(user["_id"])
    entries = await db.daily_entries.find(
        {"user_id": uid, "vital_key": {"$in": req.vital_keys}, "date": {"$gte": req.start_date, "$lte": req.end_date}},
        {"_id": 0}
    ).sort("date", 1).to_list(10000)
    if req.format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Vital", "Value", "Value2", "Unit", "Notes"])
        for e in entries:
            vtype = next((v for v in VITAL_TYPES if v["key"] == e["vital_key"]), {})
            writer.writerow([e["date"], vtype.get("name", e["vital_key"]), e.get("value", ""), e.get("value2", ""), vtype.get("unit", ""), e.get("notes", "")])
        output.seek(0)
        # Log export
        await db.exports.insert_one({"user_id": uid, "type": "csv", "vital_keys": req.vital_keys, "start_date": req.start_date, "end_date": req.end_date, "created_at": datetime.now(timezone.utc).isoformat()})
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=vitals_{req.start_date}_{req.end_date}.csv"}
        )
    elif req.format == "pdf":
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "VitalTrack Health Report", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, f"Period: {req.start_date} to {req.end_date}", ln=True, align="C")
        pdf.cell(0, 8, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")
        pdf.ln(5)
        if plan["key"] == "free":
            pdf.set_font("Helvetica", "I", 8)
            pdf.cell(0, 6, "Free Plan - Upgrade for full reports without watermark", ln=True, align="C")
            pdf.ln(3)
        pdf.set_font("Helvetica", "B", 10)
        col_widths = [25, 40, 25, 25, 20, 55]
        headers = ["Date", "Vital", "Value", "Value2", "Unit", "Notes"]
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=1, align="C")
        pdf.ln()
        pdf.set_font("Helvetica", "", 9)
        for e in entries:
            vtype = next((v for v in VITAL_TYPES if v["key"] == e["vital_key"]), {})
            row = [e["date"], vtype.get("name", e["vital_key"])[:20], str(e.get("value", "")), str(e.get("value2", "")), vtype.get("unit", ""), (e.get("notes", "") or "")[:30]]
            for i, val in enumerate(row):
                pdf.cell(col_widths[i], 7, val, border=1)
            pdf.ln()
        buf = io.BytesIO()
        pdf.output(buf)
        buf.seek(0)
        await db.exports.insert_one({"user_id": uid, "type": "pdf", "vital_keys": req.vital_keys, "start_date": req.start_date, "end_date": req.end_date, "created_at": datetime.now(timezone.utc).isoformat()})
        return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=vitals_{req.start_date}_{req.end_date}.pdf"})
    raise HTTPException(status_code=400, detail="Invalid format")

@api_router.get("/exports")
async def list_exports(request: Request):
    user = await get_current_user(request)
    exports = await db.exports.find({"user_id": str(user["_id"])}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return exports

# ==================== REMINDER ROUTES ====================
@api_router.get("/reminders")
async def get_reminders(request: Request):
    user = await get_current_user(request)
    reminders = await db.reminders.find({"user_id": str(user["_id"])}).to_list(50)
    return [{"id": str(r["_id"]), **{k: v for k, v in r.items() if k != "_id"}} for r in reminders]

@api_router.post("/reminders")
async def create_reminder(req: ReminderRequest, request: Request):
    user = await get_current_user(request)
    doc = {"user_id": str(user["_id"]), "vital_keys": req.vital_keys, "time": req.time,
           "frequency": req.frequency, "enabled": req.enabled,
           "created_at": datetime.now(timezone.utc).isoformat()}
    result = await db.reminders.insert_one(doc)
    return {"id": str(result.inserted_id), "message": "Reminder created"}

@api_router.put("/reminders/{reminder_id}")
async def update_reminder(reminder_id: str, req: ReminderRequest, request: Request):
    user = await get_current_user(request)
    result = await db.reminders.update_one(
        {"_id": ObjectId(reminder_id), "user_id": str(user["_id"])},
        {"$set": {"vital_keys": req.vital_keys, "time": req.time, "frequency": req.frequency, "enabled": req.enabled}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder updated"}

@api_router.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.reminders.delete_one({"_id": ObjectId(reminder_id), "user_id": str(user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted"}

# ==================== SHARED REPORTS ====================
@api_router.post("/shared-reports")
async def create_shared_report(req: SharedReportRequest, request: Request):
    user = await get_current_user(request)
    plan = get_user_plan(user)
    if not plan["sharing"]:
        raise HTTPException(status_code=403, detail="Sharing requires Standard or Premium plan")
    token = secrets.token_urlsafe(24)
    doc = {"user_id": str(user["_id"]), "token": token, "vital_keys": req.vital_keys,
           "start_date": req.start_date, "end_date": req.end_date,
           "expires_at": (datetime.now(timezone.utc) + timedelta(days=req.expires_days)).isoformat(),
           "password_hash": hash_password(req.password) if req.password else None,
           "has_password": bool(req.password),
           "active": True, "created_at": datetime.now(timezone.utc).isoformat()}
    await db.shared_reports.insert_one(doc)
    return {"token": token, "message": "Shared report created", "has_password": bool(req.password)}

@api_router.get("/shared-reports")
async def list_shared_reports(request: Request):
    user = await get_current_user(request)
    reports = await db.shared_reports.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(50)
    return [{"id": str(r["_id"]), **{k: v for k, v in r.items() if k != "_id"}} for r in reports]

@api_router.get("/shared-reports/view/{token}")
async def view_shared_report(token: str):
    report = await db.shared_reports.find_one({"token": token, "active": True})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or expired")
    if report.get("expires_at"):
        exp = report["expires_at"]
        if isinstance(exp, str):
            exp = datetime.fromisoformat(exp)
        if datetime.now(timezone.utc) > exp:
            raise HTTPException(status_code=410, detail="Report link has expired")
    # If password protected, return metadata only
    if report.get("has_password"):
        return {"requires_password": True, "vital_keys": report["vital_keys"],
                "start_date": report["start_date"], "end_date": report["end_date"]}
    entries = await db.daily_entries.find(
        {"user_id": report["user_id"], "vital_key": {"$in": report["vital_keys"]},
         "date": {"$gte": report["start_date"], "$lte": report["end_date"]}},
        {"_id": 0}
    ).sort("date", 1).to_list(5000)
    user = await db.users.find_one({"_id": ObjectId(report["user_id"])})
    return {"entries": entries, "vital_keys": report["vital_keys"],
            "start_date": report["start_date"], "end_date": report["end_date"],
            "user_name": user.get("name", "User") if user else "User",
            "vital_types": [v for v in VITAL_TYPES if v["key"] in report["vital_keys"]]}

@api_router.post("/shared-reports/view/{token}")
async def view_shared_report_with_password(token: str, req: SharedReportAccessRequest):
    report = await db.shared_reports.find_one({"token": token, "active": True})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or expired")
    if report.get("expires_at"):
        exp = report["expires_at"]
        if isinstance(exp, str):
            exp = datetime.fromisoformat(exp)
        if datetime.now(timezone.utc) > exp:
            raise HTTPException(status_code=410, detail="Report link has expired")
    if report.get("has_password") and report.get("password_hash"):
        if not req.password or not verify_password(req.password, report["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect password")
    entries = await db.daily_entries.find(
        {"user_id": report["user_id"], "vital_key": {"$in": report["vital_keys"]},
         "date": {"$gte": report["start_date"], "$lte": report["end_date"]}},
        {"_id": 0}
    ).sort("date", 1).to_list(5000)
    user = await db.users.find_one({"_id": ObjectId(report["user_id"])})
    return {"entries": entries, "vital_keys": report["vital_keys"],
            "start_date": report["start_date"], "end_date": report["end_date"],
            "user_name": user.get("name", "User") if user else "User",
            "vital_types": [v for v in VITAL_TYPES if v["key"] in report["vital_keys"]]}

@api_router.delete("/shared-reports/{report_id}")
async def revoke_shared_report(report_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.shared_reports.update_one(
        {"_id": ObjectId(report_id), "user_id": str(user["_id"])},
        {"$set": {"active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report revoked"}

# ==================== ADMIN ROUTES ====================
@api_router.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    await get_admin_user(request)
    total_users = await db.users.count_documents({})
    free_users = await db.users.count_documents({"plan": "free"})
    standard_users = await db.users.count_documents({"plan": "standard"})
    premium_users = await db.users.count_documents({"plan": "premium"})
    total_entries = await db.daily_entries.count_documents({})
    total_exports = await db.exports.count_documents({})
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entries_today = await db.daily_entries.count_documents({"date": today})
    # Vital usage
    pipeline = [{"$group": {"_id": "$vital_key", "count": {"$sum": 1}}}]
    vital_usage = {}
    async for doc in db.daily_entries.aggregate(pipeline):
        vital_usage[doc["_id"]] = doc["count"]
    # MRR calculation
    mrr = (standard_users * 299) + (premium_users * 499)
    return {
        "total_users": total_users, "free_users": free_users, "standard_users": standard_users,
        "premium_users": premium_users, "total_entries": total_entries, "total_exports": total_exports,
        "entries_today": entries_today, "vital_usage": vital_usage, "mrr": mrr, "arr": mrr * 12
    }

@api_router.get("/admin/users")
async def admin_list_users(request: Request, skip: int = 0, limit: int = 50, search: str = ""):
    await get_admin_user(request)
    query = {}
    if search:
        query = {"$or": [{"email": {"$regex": search, "$options": "i"}}, {"name": {"$regex": search, "$options": "i"}}]}
    total = await db.users.count_documents(query)
    users = await db.users.find(query).skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
    return {"users": [serialize_user(u) for u in users], "total": total, "skip": skip, "limit": limit}

@api_router.get("/admin/users/{user_id}")
async def admin_get_user(user_id: str, request: Request):
    await get_admin_user(request)
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    entries_count = await db.daily_entries.count_documents({"user_id": user_id})
    exports_count = await db.exports.count_documents({"user_id": user_id})
    return {**serialize_user(user), "entries_count": entries_count, "exports_count": exports_count}

@api_router.put("/admin/users/{user_id}")
async def admin_update_user(user_id: str, request: Request):
    admin = await get_admin_user(request)
    body = await request.json()
    allowed = ["name", "role", "plan", "enabled_vitals"]
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    await db.audit_logs.insert_one({"user_id": str(admin["_id"]), "action": "admin_update_user", "details": f"Updated user {user_id}: {list(updates.keys())}", "created_at": datetime.now(timezone.utc)})
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return serialize_user(user)

@api_router.get("/admin/plans")
async def admin_list_plans(request: Request):
    await get_admin_user(request)
    plans = await db.plans.find({}, {"_id": 0}).to_list(10)
    return plans

@api_router.put("/admin/plans/{plan_key}")
async def admin_update_plan(plan_key: str, request: Request):
    await get_admin_user(request)
    body = await request.json()
    allowed = ["name", "price", "price_yearly", "vital_limit", "chart_history_days", "csv_export", "pdf_export", "sharing", "features"]
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    await db.plans.update_one({"key": plan_key}, {"$set": updates})
    return {"message": f"Plan {plan_key} updated"}

@api_router.get("/admin/analytics")
async def admin_analytics(request: Request):
    await get_admin_user(request)
    # Entries per day (last 30 days)
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    pipeline = [
        {"$match": {"date": {"$gte": thirty_days_ago}}},
        {"$group": {"_id": "$date", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    daily_entries = []
    async for doc in db.daily_entries.aggregate(pipeline):
        daily_entries.append({"date": doc["_id"], "count": doc["count"]})
    # Registrations per day
    reg_pipeline = [
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    registrations = []
    try:
        async for doc in db.users.aggregate(reg_pipeline):
            registrations.append({"date": doc["_id"], "count": doc["count"]})
    except Exception:
        pass
    # Recent audit logs
    logs = await db.audit_logs.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    for log in logs:
        if isinstance(log.get("created_at"), datetime):
            log["created_at"] = log["created_at"].isoformat()
    return {"daily_entries": daily_entries, "registrations": registrations, "audit_logs": logs}

# ==================== RAZORPAY ROUTES ====================
@api_router.post("/razorpay/create-order")
async def razorpay_create_order(req: RazorpayOrderRequest, request: Request):
    user = await get_current_user(request)
    if not razorpay_client:
        raise HTTPException(status_code=503, detail="Razorpay not configured")
    plan = next((p for p in PLANS if p["key"] == req.plan_key), None)
    if not plan or plan["price"] == 0:
        raise HTTPException(status_code=400, detail="Invalid plan for payment")
    price = plan["price_yearly"] if req.billing_cycle == "yearly" else plan["price"]
    amount_paise = int(price * 100)
    try:
        order = razorpay_client.order.create({
            "amount": amount_paise, "currency": "INR", "payment_capture": 1,
            "notes": {"user_id": str(user["_id"]), "plan_key": req.plan_key, "billing_cycle": req.billing_cycle}
        })
        await db.payment_transactions.insert_one({
            "user_id": str(user["_id"]), "order_id": order["id"], "plan_key": req.plan_key,
            "amount": price, "currency": "INR", "billing_cycle": req.billing_cycle,
            "status": "created", "gateway": "razorpay",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        return {"order_id": order["id"], "amount": amount_paise, "currency": "INR",
                "key_id": RAZORPAY_KEY_ID, "plan": plan}
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {e}")
        raise HTTPException(status_code=500, detail="Payment order creation failed")

@api_router.post("/razorpay/verify-payment")
async def razorpay_verify_payment(req: RazorpayVerifyRequest, request: Request):
    user = await get_current_user(request)
    uid = str(user["_id"])
    if not razorpay_client:
        raise HTTPException(status_code=503, detail="Razorpay not configured")
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": req.razorpay_order_id,
            "razorpay_payment_id": req.razorpay_payment_id,
            "razorpay_signature": req.razorpay_signature
        })
    except Exception:
        raise HTTPException(status_code=400, detail="Payment verification failed")
    # Activate plan
    new_plan = next((p for p in PLANS if p["key"] == req.plan_key), None)
    if not new_plan:
        raise HTTPException(status_code=400, detail="Invalid plan")
    enabled = user.get("enabled_vitals", [])
    if new_plan["vital_limit"] < len(enabled):
        enabled = enabled[:new_plan["vital_limit"]]
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"plan": req.plan_key, "enabled_vitals": enabled, "updated_at": datetime.now(timezone.utc).isoformat()}})
    await db.subscriptions.update_one(
        {"user_id": uid, "status": "active"},
        {"$set": {"plan_key": req.plan_key, "status": "active", "gateway": "razorpay",
                  "payment_id": req.razorpay_payment_id, "order_id": req.razorpay_order_id,
                  "started_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    await db.payment_transactions.update_one(
        {"order_id": req.razorpay_order_id},
        {"$set": {"payment_id": req.razorpay_payment_id, "status": "captured"}}
    )
    await db.audit_logs.insert_one({"user_id": uid, "action": "payment_success", "details": f"Razorpay: {req.plan_key}", "created_at": datetime.now(timezone.utc)})
    return {"message": f"Payment successful! Plan upgraded to {new_plan['name']}", "plan": new_plan, "enabled_vitals": enabled}

@api_router.post("/razorpay/webhook")
async def razorpay_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    webhook_secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET", RAZORPAY_KEY_SECRET)
    try:
        expected = hmac.new(webhook_secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            logger.warning("Razorpay webhook signature mismatch")
    except Exception:
        pass
    try:
        data = json.loads(payload)
        event = data.get("event", "")
        logger.info(f"Razorpay webhook event: {event}")
        if event == "payment.captured":
            payment = data.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = payment.get("order_id")
            if order_id:
                await db.payment_transactions.update_one(
                    {"order_id": order_id},
                    {"$set": {"status": "captured", "payment_id": payment.get("id")}}
                )
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
    return {"status": "ok"}

# ==================== TRANSLATIONS ROUTES ====================
@api_router.get("/translations/{lang}")
async def get_translations(lang: str):
    if lang not in TRANSLATIONS:
        lang = "en"
    return TRANSLATIONS[lang]

@api_router.get("/translations")
async def list_languages():
    return {"languages": [
        {"code": "en", "name": "English", "native": "English"},
        {"code": "hi", "name": "Hindi", "native": "हिन्दी"},
        {"code": "te", "name": "Telugu", "native": "తెలుగు"},
    ]}

# ==================== APP CONFIG ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ.get("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
        "https://wellness-log-105.preview.emergentagent.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
