from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
import secrets

from config import db
from utils import get_current_user

router = APIRouter()

@router.get("/referral")
async def get_referral_info(request: Request):
    user = await get_current_user(request)
    uid = str(user["_id"])
    code = user.get("referral_code")
    if not code:
        code = f"VT{secrets.token_hex(4).upper()}"
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"referral_code": code}})
    referrals = await db.referrals.find({"referrer_id": uid}, {"_id": 0}).to_list(100)
    return {"referral_code": code, "referrals": referrals,
            "total_referrals": len(referrals), "successful_referrals": len([r for r in referrals if r.get("status") == "completed"])}

@router.post("/referral/apply")
async def apply_referral(request: Request):
    body = await request.json()
    code = body.get("code", "").strip().upper()
    user = await get_current_user(request)
    uid = str(user["_id"])
    if user.get("referred_by"):
        raise HTTPException(status_code=400, detail="You already used a referral code")
    referrer = await db.users.find_one({"referral_code": code})
    if not referrer:
        raise HTTPException(status_code=404, detail="Invalid referral code")
    if str(referrer["_id"]) == uid:
        raise HTTPException(status_code=400, detail="Cannot refer yourself")
    now = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"plan": "standard", "referred_by": code, "referral_reward_until": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()}})
    await db.users.update_one({"_id": referrer["_id"]}, {"$set": {"plan": "standard", "referral_reward_until": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()}})
    await db.referrals.insert_one({"referrer_id": str(referrer["_id"]), "referee_id": uid, "code": code, "status": "completed", "created_at": now})
    await db.audit_logs.insert_one({"user_id": uid, "action": "referral_applied", "details": f"Code: {code}", "created_at": datetime.now(timezone.utc)})
    return {"message": "Referral applied! Both you and your friend get 1 month of Standard plan free."}
