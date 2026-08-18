from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
import httpx
import secrets

from config import db, VITAL_KEYS, logger
from utils import serialize_user, create_access_token, create_refresh_token, set_auth_cookies

router = APIRouter()

EMERGENT_AUTH_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"


@router.post("/auth/google/callback")
async def google_auth_callback(request: Request, response: Response):
    """Exchange Emergent session_id for user session. Creates or links user."""
    body = await request.json()
    session_id = body.get("session_id", "").strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    # Call Emergent Auth to get user data
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(EMERGENT_AUTH_URL, headers={"X-Session-ID": session_id})
            if res.status_code != 200:
                logger.error(f"Emergent Auth error: {res.status_code} {res.text}")
                raise HTTPException(status_code=401, detail="Google authentication failed")
            google_data = res.json()
    except httpx.RequestError as e:
        logger.error(f"Emergent Auth request failed: {e}")
        raise HTTPException(status_code=502, detail="Authentication service unavailable")

    email = google_data.get("email", "").lower().strip()
    name = google_data.get("name", "")
    picture = google_data.get("picture", "")
    google_id = google_data.get("id", "")
    emergent_session_token = google_data.get("session_token", "")

    if not email:
        raise HTTPException(status_code=400, detail="No email received from Google")

    # Check if user already exists by email
    existing_user = await db.users.find_one({"email": email})

    if existing_user:
        # Link Google to existing account
        updates = {"google_id": google_id, "updated_at": datetime.now(timezone.utc)}
        if picture and not existing_user.get("picture"):
            updates["picture"] = picture
        if name and not existing_user.get("name"):
            updates["name"] = name
        await db.users.update_one({"_id": existing_user["_id"]}, {"$set": updates})
        user = await db.users.find_one({"_id": existing_user["_id"]})
    else:
        # Create new user from Google data
        user_doc = {
            "email": email,
            "password_hash": "",  # No password for Google-only users
            "name": name,
            "picture": picture,
            "google_id": google_id,
            "role": "user",
            "plan": "free",
            "enabled_vitals": [],
            "settings": {"language": "en"},
            "referral_code": f"VT{secrets.token_hex(4).upper()}",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        user = user_doc

    user_id = str(user["_id"])

    # Store Emergent session token for verification
    await db.google_sessions.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "session_token": emergent_session_token,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            "created_at": datetime.now(timezone.utc),
        }},
        upsert=True,
    )

    # Set JWT cookies (same as email/password login)
    access = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    set_auth_cookies(response, access, refresh)

    await db.audit_logs.insert_one({
        "user_id": user_id,
        "action": "google_login",
        "details": f"Google OAuth login: {email}",
        "created_at": datetime.now(timezone.utc),
    })

    return serialize_user(user)
