import bcrypt
import jwt as pyjwt
import secrets
import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException, Request, Response
from bson import ObjectId
from datetime import datetime, timezone, timedelta

from config import db, JWT_SECRET, JWT_ALGORITHM, PLANS, logger


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

async def send_email(to_email: str, subject: str, html_body: str):
    smtp_settings = await db.settings.find_one({"key": "smtp"})
    if not smtp_settings or not smtp_settings.get("smtp_host") or not smtp_settings.get("smtp_username"):
        logger.warning("SMTP not configured, skipping email send")
        return False
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{smtp_settings.get('smtp_from_name', 'VitalTrack')} <{smtp_settings.get('smtp_from_email', smtp_settings['smtp_username'])}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))
    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_settings["smtp_host"],
            port=smtp_settings.get("smtp_port", 587),
            username=smtp_settings["smtp_username"],
            password=smtp_settings.get("smtp_password", ""),
            use_tls=smtp_settings.get("smtp_use_tls", True),
        )
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

async def check_and_send_reminders():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        users_cursor = db.users.find({"role": {"$ne": "super_admin"}})
        async for user in users_cursor:
            uid = str(user["_id"])
            enabled = user.get("enabled_vitals", [])
            if not enabled:
                continue
            reminder = await db.reminders.find_one({"user_id": uid, "enabled": True})
            if not reminder:
                continue
            entry = await db.daily_entries.find_one({"user_id": uid, "date": today})
            if entry:
                continue
            email = user.get("email", "")
            name = user.get("name", "there")
            html = f"""
            <div style="font-family:Arial,sans-serif;max-width:500px;margin:0 auto;padding:24px;">
                <h2 style="color:#0EA5E9;">Hi {name},</h2>
                <p style="color:#6E6E6A;">You haven't logged your health vitals today.</p>
                <a href="{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/tracker" style="display:inline-block;background:#0EA5E9;color:white;padding:12px 24px;border-radius:24px;text-decoration:none;margin-top:12px;">Log Vitals Now</a>
            </div>"""
            await send_email(email, "Reminder: Log your health vitals today", html)
            await db.audit_logs.insert_one({"user_id": uid, "action": "email_reminder_sent", "details": f"Daily reminder sent to {email}", "created_at": datetime.now(timezone.utc)})
    except Exception as e:
        logger.error(f"Reminder job error: {e}")

async def record_coupon_usage(user_id: str, code: str):
    await db.coupon_usage.insert_one({"user_id": user_id, "code": code, "used_at": datetime.now(timezone.utc).isoformat()})
    await db.coupons.update_one({"code": code}, {"$inc": {"used_count": 1}})
