from config import db, VITAL_TYPES, VITAL_KEYS, PLANS, scheduler, client, logger
from utils import hash_password, verify_password, check_and_send_reminders

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime, timezone
import os

app = FastAPI(title="VitalTrack API")
api_router = APIRouter(prefix="/api")

# Import route modules
from routes.auth import router as auth_router
from routes.vitals import router as vitals_router
from routes.exports import router as exports_router
from routes.sharing import router as sharing_router
from routes.referral import router as referral_router
from routes.push import router as push_router
from routes.content import router as content_router
from routes.payments import router as payments_router
from routes.admin import router as admin_router
from routes.sync import router as sync_router
from routes.google_auth import router as google_auth_router

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(vitals_router)
api_router.include_router(exports_router)
api_router.include_router(sharing_router)
api_router.include_router(referral_router)
api_router.include_router(push_router)
api_router.include_router(content_router)
api_router.include_router(payments_router)
api_router.include_router(admin_router)
api_router.include_router(sync_router)
api_router.include_router(google_auth_router)


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
    await db.devices.create_index([("user_id", 1), ("device_id", 1)], unique=True)
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
    # Seed second admin from environment
    admin2_email = os.environ.get("ADMIN2_EMAIL", "")
    admin2_password = os.environ.get("ADMIN2_PASSWORD", "")
    if admin2_email and admin2_password:
        existing2 = await db.users.find_one({"email": admin2_email})
        if not existing2:
            await db.users.insert_one({
                "email": admin2_email, "password_hash": hash_password(admin2_password),
                "name": admin2_email.split("@")[0], "role": "super_admin", "plan": "premium",
                "enabled_vitals": VITAL_KEYS, "settings": {"language": "en"},
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)
            })
            logger.info(f"Admin user created: {admin2_email}")
        elif not verify_password(admin2_password, existing2["password_hash"]):
            await db.users.update_one({"email": admin2_email}, {"$set": {"password_hash": hash_password(admin2_password)}})
    # Write test credentials
    creds_dir = Path("/app/memory")
    creds_dir.mkdir(exist_ok=True)
    with open(creds_dir / "test_credentials.md", "w") as f:
        creds = f"# Test Credentials\n\n## Admin 1\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: super_admin\n"
        if admin2_email:
            creds += f"\n## Admin 2\n- Email: {admin2_email}\n- Password: {admin2_password}\n- Role: super_admin\n"
        creds += "\n## Test User\n- Register at /register with any email\n\n## Endpoints\n- Login: POST /api/auth/login\n- Register: POST /api/auth/register\n- Me: GET /api/auth/me\n"
        f.write(creds)
    logger.info("VitalTrack API started successfully")
    # Start scheduler
    if not scheduler.running:
        scheduler.start()
    # Check if reminders are enabled
    reminder_settings = await db.settings.find_one({"key": "reminders"})
    if reminder_settings and reminder_settings.get("enabled"):
        time_str = reminder_settings.get("time", "08:00")
        hour, minute = map(int, time_str.split(":"))
        scheduler.add_job(check_and_send_reminders, "cron", hour=hour, minute=minute, id="daily_reminder", replace_existing=True)
        logger.info(f"Reminder job scheduled at {time_str}")


@app.on_event("shutdown")
async def shutdown():
    if scheduler.running:
        scheduler.shutdown()
    client.close()


# CORS
_frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
_origins = list(set(filter(None, [
    _frontend_url,
    "http://localhost:3000",
    "https://wellness-log-105.preview.emergentagent.com",
])))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
