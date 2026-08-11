from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from datetime import datetime, timezone

from config import db, VITAL_TYPES, VITAL_KEYS, PLANS, scheduler, logger
from models import SmtpSettingsRequest, ContentPageRequest, CouponRequest
from utils import get_admin_user, hash_password, serialize_user, check_and_send_reminders

router = APIRouter()

@router.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    await get_admin_user(request)
    total = await db.users.count_documents({})
    free = await db.users.count_documents({"plan": "free"})
    standard = await db.users.count_documents({"plan": "standard"})
    premium = await db.users.count_documents({"plan": "premium"})
    entries = await db.daily_entries.count_documents({})
    exports = await db.exports.count_documents({})
    mrr = standard * 299 + premium * 499
    arr = mrr * 12
    vital_usage = {}
    pipeline = [{"$group": {"_id": "$vital_key", "count": {"$sum": 1}}}]
    async for doc in db.daily_entries.aggregate(pipeline):
        vital_usage[doc["_id"]] = doc["count"]
    return {"total_users": total, "free_users": free, "standard_users": standard,
            "premium_users": premium, "total_entries": entries, "total_exports": exports,
            "mrr": mrr, "arr": arr, "vital_usage": vital_usage}

@router.get("/admin/users")
async def admin_list_users(request: Request, skip: int = 0, limit: int = 50, search: str = ""):
    await get_admin_user(request)
    query = {}
    if search:
        query = {"$or": [{"email": {"$regex": search, "$options": "i"}}, {"name": {"$regex": search, "$options": "i"}}]}
    total = await db.users.count_documents(query)
    users = await db.users.find(query).skip(skip).limit(limit).to_list(limit)
    return {"users": [serialize_user(u) for u in users], "total": total}

@router.get("/admin/users/{user_id}")
async def admin_get_user(user_id: str, request: Request):
    await get_admin_user(request)
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_user(user)

@router.put("/admin/users/{user_id}")
async def admin_update_user(user_id: str, request: Request):
    await get_admin_user(request)
    body = await request.json()
    updates = {k: v for k, v in body.items() if k in ["name", "email", "role", "plan", "enabled_vitals"]}
    if "plan" in updates:
        plan = next((p for p in PLANS if p["key"] == updates["plan"]), None)
        if plan and updates["plan"] == "premium":
            updates["enabled_vitals"] = VITAL_KEYS
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    return {"message": "User updated"}

@router.post("/admin/users")
async def admin_create_user(request: Request):
    await get_admin_user(request)
    body = await request.json()
    email = body.get("email", "").lower().strip()
    password = body.get("password", "")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    import secrets
    user_doc = {
        "email": email, "password_hash": hash_password(password),
        "name": body.get("name", ""), "role": body.get("role", "user"),
        "plan": body.get("plan", "free"), "enabled_vitals": [],
        "settings": {"language": "en"},
        "referral_code": f"VT{secrets.token_hex(4).upper()}",
        "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)
    }
    if user_doc["plan"] == "premium":
        user_doc["enabled_vitals"] = VITAL_KEYS
    elif user_doc["plan"] == "standard":
        user_doc["enabled_vitals"] = VITAL_KEYS[:6]
    result = await db.users.insert_one(user_doc)
    return {"id": str(result.inserted_id), "message": "User created"}

@router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, request: Request):
    admin = await get_admin_user(request)
    if str(admin["_id"]) == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.daily_entries.delete_many({"user_id": user_id})
    await db.reminders.delete_many({"user_id": user_id})
    await db.exports.delete_many({"user_id": user_id})
    await db.shared_reports.delete_many({"user_id": user_id})
    await db.audit_logs.insert_one({"user_id": str(admin["_id"]), "action": "user_deleted",
                                     "details": f"Deleted user {user.get('email', user_id)}",
                                     "created_at": datetime.now(timezone.utc)})
    return {"message": "User deleted"}

@router.get("/admin/plans")
async def admin_list_plans(request: Request):
    await get_admin_user(request)
    return PLANS

@router.put("/admin/plans/{plan_key}")
async def admin_update_plan(plan_key: str, request: Request):
    await get_admin_user(request)
    body = await request.json()
    result = await db.plans.update_one({"key": plan_key}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan updated"}

@router.get("/admin/analytics")
async def admin_analytics(request: Request):
    await get_admin_user(request)
    daily_entries = []
    pipeline = [
        {"$group": {"_id": "$date", "count": {"$sum": 1}}},
        {"$sort": {"_id": -1}}, {"$limit": 30}
    ]
    async for doc in db.daily_entries.aggregate(pipeline):
        daily_entries.append({"date": doc["_id"], "count": doc["count"]})
    daily_entries.reverse()
    audit_logs = await db.audit_logs.find({}).sort("created_at", -1).limit(50).to_list(50)
    for log in audit_logs:
        log["_id"] = str(log["_id"])
        if "created_at" in log and isinstance(log["created_at"], datetime):
            log["created_at"] = log["created_at"].isoformat()
    return {"daily_entries": daily_entries, "audit_logs": audit_logs}

# SMTP Settings
@router.get("/admin/smtp-settings")
async def get_smtp_settings(request: Request):
    await get_admin_user(request)
    settings = await db.settings.find_one({"key": "smtp"}, {"_id": 0})
    if settings and "smtp_password" in settings:
        settings["smtp_password"] = "********" if settings["smtp_password"] else ""
    return settings or {"key": "smtp"}

@router.put("/admin/smtp-settings")
async def update_smtp_settings(req: SmtpSettingsRequest, request: Request):
    await get_admin_user(request)
    updates = {k: v for k, v in req.dict().items() if v is not None}
    current = await db.settings.find_one({"key": "smtp"})
    if updates.get("smtp_password") == "********" and current:
        updates["smtp_password"] = current.get("smtp_password", "")
    updates["key"] = "smtp"
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.settings.update_one({"key": "smtp"}, {"$set": updates}, upsert=True)
    return {"message": "SMTP settings saved"}

# Reminder Settings
@router.post("/admin/send-reminders")
async def admin_send_reminders(request: Request):
    await get_admin_user(request)
    await check_and_send_reminders()
    return {"message": "Reminder check completed"}

@router.get("/admin/reminder-settings")
async def get_reminder_settings(request: Request):
    await get_admin_user(request)
    settings = await db.settings.find_one({"key": "reminders"}, {"_id": 0})
    return settings or {"key": "reminders", "enabled": False, "time": "09:00"}

@router.put("/admin/reminder-settings")
async def update_reminder_settings(request: Request):
    await get_admin_user(request)
    body = await request.json()
    enabled = body.get("enabled", False)
    time_str = body.get("time", "09:00")
    await db.settings.update_one(
        {"key": "reminders"},
        {"$set": {"key": "reminders", "enabled": enabled, "time": time_str, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    if enabled:
        hour, minute = map(int, time_str.split(":"))
        scheduler.add_job(check_and_send_reminders, "cron", hour=hour, minute=minute, id="daily_reminder", replace_existing=True)
    else:
        try:
            scheduler.remove_job("daily_reminder")
        except Exception:
            pass
    return {"message": f"Reminders {'enabled' if enabled else 'disabled'}"}

# Content Page Management
@router.get("/admin/content-pages")
async def admin_list_content_pages(request: Request):
    await get_admin_user(request)
    pages = await db.content_pages.find({}, {"_id": 0}).to_list(100)
    return {"pages": pages}

@router.post("/admin/content-pages")
async def admin_create_content_page(req: ContentPageRequest, request: Request):
    await get_admin_user(request)
    doc = req.dict()
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.content_pages.update_one({"key": req.key}, {"$set": doc}, upsert=True)
    return {"message": "Content page saved"}

@router.put("/admin/content-pages/{page_key}")
async def admin_update_content_page(page_key: str, req: ContentPageRequest, request: Request):
    await get_admin_user(request)
    doc = req.dict()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.content_pages.update_one({"key": page_key}, {"$set": doc}, upsert=True)
    return {"message": "Content page updated"}

@router.delete("/admin/content-pages/{page_key}")
async def admin_delete_content_page(page_key: str, request: Request):
    await get_admin_user(request)
    result = await db.content_pages.delete_one({"key": page_key})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"message": "Content page deleted"}

# Coupon Management
@router.get("/admin/coupons")
async def admin_list_coupons(request: Request):
    await get_admin_user(request)
    coupons = await db.coupons.find({}, {"_id": 0}).to_list(100)
    return {"coupons": coupons}

@router.post("/admin/coupons")
async def admin_create_coupon(req: CouponRequest, request: Request):
    await get_admin_user(request)
    code = req.code.upper().strip()
    existing = await db.coupons.find_one({"code": code})
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    doc = {
        "code": code, "discount_percent": req.discount_percent,
        "max_uses": req.max_uses, "used_count": 0,
        "valid_plans": req.valid_plans, "expires_at": req.expires_at,
        "active": req.active, "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.coupons.insert_one(doc)
    return {"message": "Coupon created", "code": code}

@router.put("/admin/coupons/{code}")
async def admin_update_coupon(code: str, req: CouponRequest, request: Request):
    await get_admin_user(request)
    updates = {
        "discount_percent": req.discount_percent, "max_uses": req.max_uses,
        "valid_plans": req.valid_plans, "expires_at": req.expires_at,
        "active": req.active, "updated_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.coupons.update_one({"code": code.upper()}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return {"message": "Coupon updated"}

@router.delete("/admin/coupons/{code}")
async def admin_delete_coupon(code: str, request: Request):
    await get_admin_user(request)
    result = await db.coupons.delete_one({"code": code.upper()})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return {"message": "Coupon deleted"}

# Coupon validation (public, for billing page)
@router.post("/coupons/validate")
async def validate_coupon(request: Request):
    user = await get_current_user(request)
    body = await request.json()
    code = body.get("code", "").upper().strip()
    if not code:
        raise HTTPException(status_code=400, detail="Coupon code required")
    coupon = await db.coupons.find_one({"code": code})
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon code")
    if coupon.get("active") is False:
        raise HTTPException(status_code=400, detail="Coupon is inactive")
    if coupon.get("max_uses", 0) > 0 and coupon.get("used_count", 0) >= coupon["max_uses"]:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    if coupon.get("expires_at"):
        from datetime import datetime as dt
        try:
            exp = dt.fromisoformat(coupon["expires_at"].replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > exp:
                raise HTTPException(status_code=400, detail="Coupon has expired")
        except ValueError:
            pass
    existing = await db.coupon_usage.find_one({"user_id": str(user["_id"]), "code": code})
    if existing:
        raise HTTPException(status_code=400, detail="You have already used this coupon")
    return {"valid": True, "code": code, "discount_percent": coupon["discount_percent"],
            "message": f"{coupon['discount_percent']}% discount applied!"}

# Import get_current_user for coupon validation
from utils import get_current_user


# ==================== PAYMENT GATEWAY SETTINGS ====================
MASK = "********"

@router.get("/admin/payment-settings")
async def get_payment_settings(request: Request):
    await get_admin_user(request)
    settings = await db.settings.find_one({"key": "payment_gateways"}, {"_id": 0})
    if not settings:
        # Return .env values as defaults (masked)
        import os
        return {
            "key": "payment_gateways",
            "razorpay_key_id": os.environ.get("RAZORPAY_KEY_ID", ""),
            "razorpay_key_secret": MASK if os.environ.get("RAZORPAY_KEY_SECRET") else "",
            "payu_merchant_key": os.environ.get("PAYU_MERCHANT_KEY", ""),
            "payu_merchant_salt": MASK if os.environ.get("PAYU_MERCHANT_SALT") else "",
            "payu_base_url": os.environ.get("PAYU_BASE_URL", "https://test.payu.in/_payment"),
            "razorpay_configured": bool(os.environ.get("RAZORPAY_KEY_ID") and os.environ.get("RAZORPAY_KEY_SECRET")),
            "payu_configured": bool(os.environ.get("PAYU_MERCHANT_KEY") and os.environ.get("PAYU_MERCHANT_SALT")),
        }
    result = dict(settings)
    # Always return all fields consistently
    result.setdefault("razorpay_key_id", "")
    result.setdefault("payu_merchant_key", "")
    result.setdefault("payu_base_url", "https://test.payu.in/_payment")
    result["razorpay_key_secret"] = MASK if result.get("razorpay_key_secret") else ""
    result["payu_merchant_salt"] = MASK if result.get("payu_merchant_salt") else ""
    result["razorpay_configured"] = bool(result.get("razorpay_key_id") and settings.get("razorpay_key_secret"))
    result["payu_configured"] = bool(result.get("payu_merchant_key") and settings.get("payu_merchant_salt"))
    return result

@router.put("/admin/payment-settings")
async def update_payment_settings(request: Request):
    admin = await get_admin_user(request)
    body = await request.json()
    current = await db.settings.find_one({"key": "payment_gateways"})
    updates = {"key": "payment_gateways", "updated_at": datetime.now(timezone.utc).isoformat()}
    # Only update fields that are provided and not the mask
    for field in ["razorpay_key_id", "razorpay_key_secret", "payu_merchant_key", "payu_merchant_salt", "payu_base_url"]:
        val = body.get(field)
        if val is not None and val != MASK:
            updates[field] = val
        elif current and field in current:
            updates[field] = current[field]
    await db.settings.update_one({"key": "payment_gateways"}, {"$set": updates}, upsert=True)
    # Reinitialize Razorpay client if keys changed
    rzp_id = updates.get("razorpay_key_id", "")
    rzp_secret = updates.get("razorpay_key_secret", "")
    if rzp_id and rzp_secret:
        import config
        import razorpay
        config.RAZORPAY_KEY_ID = rzp_id
        config.RAZORPAY_KEY_SECRET = rzp_secret
        config.razorpay_client = razorpay.Client(auth=(rzp_id, rzp_secret))
        logger.info("Razorpay client reinitialized from admin settings")
    await db.audit_logs.insert_one({
        "user_id": str(admin["_id"]),
        "action": "payment_settings_updated",
        "details": "Payment gateway keys updated via admin panel",
        "created_at": datetime.now(timezone.utc)
    })
    return {"message": "Payment settings saved"}
