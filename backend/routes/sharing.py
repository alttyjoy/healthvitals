from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from datetime import datetime, timezone
import secrets
import bcrypt

from config import db, VITAL_TYPES, VITAL_KEYS, PLANS, logger
from models import SharedReportRequest, SharedReportAccessRequest
from utils import get_current_user, hash_password

router = APIRouter()

@router.post("/shared-reports")
async def create_shared_report(req: SharedReportRequest, request: Request):
    user = await get_current_user(request)
    uid = str(user["_id"])
    token = secrets.token_urlsafe(24)
    doc = {
        "user_id": uid, "token": token, "vital_keys": req.vital_keys,
        "start_date": req.start_date, "end_date": req.end_date,
        "expires_at": datetime.now(timezone.utc).isoformat() if req.expires_days == 0 else (datetime.now(timezone.utc) + __import__('datetime').timedelta(days=req.expires_days)).isoformat(),
        "has_password": bool(req.password), "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    if req.password:
        doc["password_hash"] = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    await db.shared_reports.insert_one(doc)
    return {"token": token, "message": "Shared report created"}

@router.get("/shared-reports")
async def list_shared_reports(request: Request):
    user = await get_current_user(request)
    reports = await db.shared_reports.find({"user_id": str(user["_id"]), "active": True}).to_list(50)
    return [{"id": str(r["_id"]), "token": r["token"], "vital_keys": r["vital_keys"],
             "start_date": r["start_date"], "end_date": r["end_date"],
             "has_password": r.get("has_password", False), "active": r.get("active", True),
             "expires_at": r.get("expires_at"), "created_at": r.get("created_at")} for r in reports]

@router.get("/shared/{token}")
async def view_shared_report(token: str):
    report = await db.shared_reports.find_one({"token": token, "active": True})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or expired")
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
            "user_name": user.get("name", "User") if user else "User", "vital_types": VITAL_TYPES}

@router.post("/shared/{token}")
async def view_shared_report_with_password(token: str, req: SharedReportAccessRequest):
    report = await db.shared_reports.find_one({"token": token, "active": True})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or expired")
    if report.get("has_password"):
        if not req.password or not bcrypt.checkpw(req.password.encode("utf-8"), report["password_hash"].encode("utf-8")):
            raise HTTPException(status_code=401, detail="Incorrect password")
    entries = await db.daily_entries.find(
        {"user_id": report["user_id"], "vital_key": {"$in": report["vital_keys"]},
         "date": {"$gte": report["start_date"], "$lte": report["end_date"]}},
        {"_id": 0}
    ).sort("date", 1).to_list(5000)
    user = await db.users.find_one({"_id": ObjectId(report["user_id"])})
    return {"entries": entries, "vital_keys": report["vital_keys"],
            "start_date": report["start_date"], "end_date": report["end_date"],
            "user_name": user.get("name", "User") if user else "User", "vital_types": VITAL_TYPES}

@router.delete("/shared-reports/{report_id}")
async def revoke_shared_report(report_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.shared_reports.update_one(
        {"_id": ObjectId(report_id), "user_id": str(user["_id"])},
        {"$set": {"active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Share link revoked"}
