from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from datetime import datetime, timezone
import hashlib
import hmac
import os

from config import db, PLANS, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, razorpay_client, logger
from models import RazorpayOrderRequest, RazorpayVerifyRequest, PlanChangeRequest, PayUInitRequest
from utils import get_current_user, get_user_plan, record_coupon_usage

router = APIRouter()

@router.get("/plans")
async def get_plans():
    return PLANS

@router.get("/subscription")
async def get_subscription(request: Request):
    user = await get_current_user(request)
    plan = get_user_plan(user)
    return {"plan": plan, "user_plan": user.get("plan", "free"),
            "subscription_start": user.get("subscription_start"),
            "subscription_end": user.get("subscription_end")}

@router.post("/subscription/change")
async def change_subscription(req: PlanChangeRequest, request: Request):
    user = await get_current_user(request)
    target = next((p for p in PLANS if p["key"] == req.plan_key), None)
    if not target:
        raise HTTPException(status_code=400, detail="Invalid plan")
    updates = {"plan": req.plan_key, "updated_at": datetime.now(timezone.utc).isoformat()}
    if req.plan_key == "free":
        enabled = user.get("enabled_vitals", [])
        if len(enabled) > target["vital_limit"]:
            updates["enabled_vitals"] = enabled[:target["vital_limit"]]
    await db.users.update_one({"_id": user["_id"]}, {"$set": updates})
    await db.audit_logs.insert_one({"user_id": str(user["_id"]), "action": "plan_change",
                                     "details": f"{user.get('plan', 'free')} -> {req.plan_key}",
                                     "created_at": datetime.now(timezone.utc)})
    return {"message": f"Plan changed to {target['name']}"}

@router.post("/razorpay/create-order")
async def razorpay_create_order(req: RazorpayOrderRequest, request: Request):
    if not razorpay_client:
        raise HTTPException(status_code=500, detail="Payment gateway not configured")
    user = await get_current_user(request)
    plan = next((p for p in PLANS if p["key"] == req.plan_key), None)
    if not plan or plan["price"] == 0:
        raise HTTPException(status_code=400, detail="Invalid plan for payment")
    amount = plan["price"] if req.billing_cycle == "monthly" else plan["price_yearly"]
    if req.coupon_code:
        coupon = await db.coupons.find_one({"code": req.coupon_code.upper(), "active": {"$ne": False}})
        if coupon:
            discount = coupon.get("discount_percent", 0)
            amount = round(amount * (1 - discount / 100))
    order_data = {"amount": amount * 100, "currency": "INR",
                  "notes": {"plan": req.plan_key, "user_id": str(user["_id"]), "cycle": req.billing_cycle, "coupon": req.coupon_code}}
    try:
        order = razorpay_client.order.create(data=order_data)
        return {"order_id": order["id"], "amount": amount, "currency": "INR",
                "key_id": RAZORPAY_KEY_ID, "plan": plan}
    except Exception as e:
        logger.error(f"Razorpay order error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment order")

@router.post("/razorpay/verify")
async def razorpay_verify_payment(req: RazorpayVerifyRequest, request: Request):
    if not razorpay_client:
        raise HTTPException(status_code=500, detail="Payment gateway not configured")
    user = await get_current_user(request)
    try:
        params = {"razorpay_order_id": req.razorpay_order_id,
                  "razorpay_payment_id": req.razorpay_payment_id,
                  "razorpay_signature": req.razorpay_signature}
        razorpay_client.utility.verify_payment_signature(params)
    except Exception:
        raise HTTPException(status_code=400, detail="Payment verification failed")
    plan = next((p for p in PLANS if p["key"] == req.plan_key), None)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")
    now = datetime.now(timezone.utc)
    await db.users.update_one({"_id": user["_id"]}, {"$set": {
        "plan": req.plan_key, "subscription_start": now.isoformat(),
        "subscription_end": (now + __import__('datetime').timedelta(days=365 if 'yearly' in req.razorpay_order_id else 30)).isoformat(),
        "updated_at": now.isoformat()
    }})
    if req.plan_key == "premium":
        from config import VITAL_KEYS
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"enabled_vitals": VITAL_KEYS}})
    await db.payments.insert_one({
        "user_id": str(user["_id"]), "provider": "razorpay",
        "order_id": req.razorpay_order_id, "payment_id": req.razorpay_payment_id,
        "plan": req.plan_key, "created_at": now.isoformat()
    })
    if req.coupon_code:
        await record_coupon_usage(str(user["_id"]), req.coupon_code.upper())
    await db.audit_logs.insert_one({"user_id": str(user["_id"]), "action": "payment_success",
                                     "details": f"Razorpay: {req.plan_key}",
                                     "created_at": now})
    return {"message": "Payment verified and plan updated", "plan": req.plan_key}

@router.post("/razorpay/webhook")
async def razorpay_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Razorpay-Signature", "")
    try:
        razorpay_client.utility.verify_webhook_signature(body.decode(), sig, RAZORPAY_KEY_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    import json
    data = json.loads(body)
    event = data.get("event", "")
    logger.info(f"Razorpay webhook: {event}")
    return {"status": "ok"}

# PayU Integration
def generate_payu_hash(params: dict, salt: str) -> str:
    hash_string = f"{params['key']}|{params['txnid']}|{params['amount']}|{params['productinfo']}|{params['firstname']}|{params['email']}|||||||||||{salt}"
    return hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

def verify_payu_hash(response_hash: str, params: dict, salt: str) -> bool:
    reverse_string = f"{salt}|{params.get('status', '')}|||||||||||{params.get('email', '')}|{params.get('firstname', '')}|{params.get('productinfo', '')}|{params.get('amount', '')}|{params.get('txnid', '')}|{params.get('key', '')}"
    calculated = hashlib.sha512(reverse_string.encode('utf-8')).hexdigest()
    return calculated == response_hash

@router.post("/payu/initiate")
async def payu_initiate(req: PayUInitRequest, request: Request):
    user = await get_current_user(request)
    plan = next((p for p in PLANS if p["key"] == req.plan_key), None)
    if not plan or plan["price"] == 0:
        raise HTTPException(status_code=400, detail="Invalid plan for payment")
    payu_key = os.environ.get("PAYU_MERCHANT_KEY", "")
    payu_salt = os.environ.get("PAYU_MERCHANT_SALT", "")
    if not payu_key or not payu_salt:
        raise HTTPException(status_code=500, detail="PayU not configured")
    amount = plan["price"] if req.billing_cycle == "monthly" else plan["price_yearly"]
    if req.coupon_code:
        coupon = await db.coupons.find_one({"code": req.coupon_code.upper(), "active": {"$ne": False}})
        if coupon:
            discount = coupon.get("discount_percent", 0)
            amount = round(amount * (1 - discount / 100))
    import secrets as sec
    txnid = f"VT{sec.token_hex(8).upper()}"
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    backend_url = frontend_url  # Same domain, backend routes are at /api/*
    params = {
        "key": payu_key, "txnid": txnid,
        "amount": str(float(amount)), "productinfo": f"VitalTrack {plan['name']} Plan",
        "firstname": user.get("name", "User"), "email": user.get("email", ""),
        "phone": "", "surl": f"{backend_url}/api/payu/callback",
        "furl": f"{backend_url}/api/payu/callback",
    }
    params["hash"] = generate_payu_hash(params, payu_salt)
    await db.payu_transactions.insert_one({
        "txnid": txnid, "user_id": str(user["_id"]),
        "plan": req.plan_key, "amount": amount, "billing_cycle": req.billing_cycle,
        "coupon_code": req.coupon_code, "status": "initiated",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    payu_url = os.environ.get("PAYU_BASE_URL", "https://test.payu.in/_payment")
    return {"payu_url": payu_url, "params": params}

@router.post("/payu/callback")
async def payu_callback(request: Request):
    from fastapi.responses import RedirectResponse
    form = await request.form()
    data = dict(form)
    payu_salt = os.environ.get("PAYU_MERCHANT_SALT", "")
    txnid = data.get("txnid", "")
    status = data.get("status", "")
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    logger.info(f"PayU callback: txnid={txnid}, status={status}")
    tx = await db.payu_transactions.find_one({"txnid": txnid})
    if not tx:
        return RedirectResponse(url=f"{frontend_url}/billing?payu=failure", status_code=303)
    if status == "success":
        response_hash = data.get("hash", "")
        if not verify_payu_hash(response_hash, data, payu_salt):
            logger.warning(f"PayU hash mismatch for txnid={txnid}")
        await db.payu_transactions.update_one({"txnid": txnid}, {"$set": {"status": "success", "payu_data": data}})
        now = datetime.now(timezone.utc)
        user_id = tx["user_id"]
        plan_key = tx["plan"]
        await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {
            "plan": plan_key, "subscription_start": now.isoformat(),
            "subscription_end": (now + __import__('datetime').timedelta(days=365 if tx.get("billing_cycle") == "yearly" else 30)).isoformat(),
            "updated_at": now.isoformat()
        }})
        if plan_key == "premium":
            from config import VITAL_KEYS
            await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"enabled_vitals": VITAL_KEYS}})
        if tx.get("coupon_code"):
            await record_coupon_usage(user_id, tx["coupon_code"].upper())
        await db.audit_logs.insert_one({"user_id": user_id, "action": "payment_success",
                                         "details": f"PayU: {plan_key}", "created_at": now})
        return RedirectResponse(url=f"{frontend_url}/billing?payu=success", status_code=303)
    else:
        await db.payu_transactions.update_one({"txnid": txnid}, {"$set": {"status": "failed", "payu_data": data}})
        return RedirectResponse(url=f"{frontend_url}/billing?payu=failure", status_code=303)
