from fastapi import APIRouter, HTTPException, Request, Response
from bson import ObjectId
from datetime import datetime, timezone, timedelta
import secrets

from config import db, JWT_SECRET, JWT_ALGORITHM, VITAL_KEYS, logger
from models import RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, ProfileUpdateRequest
from utils import hash_password, verify_password, create_access_token, create_refresh_token, set_auth_cookies, serialize_user, get_current_user
import jwt as pyjwt

router = APIRouter()

@router.post("/auth/register")
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
        "referral_code": f"VT{secrets.token_hex(4).upper()}",
        "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    access = create_access_token(str(result.inserted_id), email)
    refresh = create_refresh_token(str(result.inserted_id))
    set_auth_cookies(response, access, refresh)
    await db.audit_logs.insert_one({"user_id": str(result.inserted_id), "action": "register", "created_at": datetime.now(timezone.utc)})
    return serialize_user(user_doc)

@router.post("/auth/login")
async def login(req: LoginRequest, request: Request, response: Response):
    email = req.email.lower().strip()
    ip = request.client.host if request.client else "unknown"
    identifier = f"{ip}:{email}"
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

@router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}

@router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return serialize_user(user)

@router.post("/auth/refresh")
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

@router.post("/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    user = await db.users.find_one({"email": req.email.lower().strip()})
    if user:
        token = secrets.token_urlsafe(32)
        await db.password_reset_tokens.insert_one({
            "token": token, "user_id": str(user["_id"]),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1), "used": False
        })
        logger.info(f"Password reset token for {req.email}: {token}")
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/auth/reset-password")
async def reset_password(req: ResetPasswordRequest):
    record = await db.password_reset_tokens.find_one({"token": req.token, "used": False})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    expires = record["expires_at"]
    if isinstance(expires, str):
        expires = datetime.fromisoformat(expires)
    if datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=400, detail="Token expired")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    await db.users.update_one({"_id": ObjectId(record["user_id"])}, {"$set": {"password_hash": hash_password(req.password)}})
    await db.password_reset_tokens.update_one({"token": req.token}, {"$set": {"used": True}})
    return {"message": "Password reset successfully"}

@router.put("/profile")
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
