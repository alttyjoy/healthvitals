from fastapi import APIRouter, HTTPException, Request
import json

from config import db, VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL, logger
from utils import get_current_user, get_admin_user
from datetime import datetime, timezone

router = APIRouter()

@router.get("/push/vapid-key")
async def get_vapid_public_key():
    return {"public_key": VAPID_PUBLIC_KEY}

@router.post("/push/subscribe")
async def push_subscribe(request: Request):
    user = await get_current_user(request)
    body = await request.json()
    subscription = body.get("subscription")
    if not subscription or not subscription.get("endpoint"):
        raise HTTPException(status_code=400, detail="Invalid subscription data")
    uid = str(user["_id"])
    await db.push_subscriptions.update_one(
        {"user_id": uid, "endpoint": subscription["endpoint"]},
        {"$set": {"user_id": uid, "subscription": subscription, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Subscribed to push notifications"}

@router.post("/push/unsubscribe")
async def push_unsubscribe(request: Request):
    user = await get_current_user(request)
    body = await request.json()
    endpoint = body.get("endpoint", "")
    uid = str(user["_id"])
    await db.push_subscriptions.delete_many({"user_id": uid, "endpoint": endpoint} if endpoint else {"user_id": uid})
    return {"message": "Unsubscribed from push notifications"}

@router.get("/push/status")
async def push_status(request: Request):
    user = await get_current_user(request)
    count = await db.push_subscriptions.count_documents({"user_id": str(user["_id"])})
    return {"subscribed": count > 0, "subscription_count": count}

@router.post("/admin/push/send")
async def admin_send_push(request: Request):
    admin = await get_admin_user(request)
    body = await request.json()
    title = body.get("title", "VitalTrack")
    message = body.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    from pywebpush import webpush, WebPushException
    subs = await db.push_subscriptions.find({}).to_list(10000)
    sent = 0
    failed = 0
    for sub in subs:
        try:
            webpush(
                subscription_info=sub["subscription"],
                data=json.dumps({"title": title, "body": message, "icon": "/logo192.png"}),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_EMAIL}
            )
            sent += 1
        except WebPushException as e:
            if "410" in str(e) or "404" in str(e):
                await db.push_subscriptions.delete_one({"_id": sub["_id"]})
            failed += 1
        except Exception:
            failed += 1
    await db.audit_logs.insert_one({"user_id": str(admin["_id"]), "action": "push_sent", "details": f"Push: '{title}' sent={sent} failed={failed}", "created_at": datetime.now(timezone.utc)})
    return {"message": f"Push sent to {sent} subscribers", "sent": sent, "failed": failed}

@router.get("/admin/push/stats")
async def admin_push_stats(request: Request):
    await get_admin_user(request)
    total = await db.push_subscriptions.count_documents({})
    return {"total_subscribers": total}
