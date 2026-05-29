from fastapi import APIRouter, HTTPException, Request, Query
from datetime import datetime, timezone, timedelta

from config import db, VITAL_TYPES, VITAL_KEYS
from models import EntryData, BulkEntryRequest, VitalToggleRequest, ReminderRequest
from utils import get_current_user, get_user_plan

router = APIRouter()

@router.get("/vitals/types")
async def get_vital_types():
    return VITAL_TYPES

@router.get("/vitals/enabled")
async def get_enabled_vitals(request: Request):
    user = await get_current_user(request)
    enabled = user.get("enabled_vitals", [])
    return {"enabled_vitals": enabled, "plan": user.get("plan", "free"), "vital_limit": get_user_plan(user)["vital_limit"]}

@router.post("/vitals/toggle")
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
            raise HTTPException(status_code=403, detail=f"Your {plan['name']} plan allows up to {plan['vital_limit']} vitals. Upgrade to enable more.")
        enabled.append(req.vital_key)
    else:
        enabled = [v for v in enabled if v != req.vital_key]
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"enabled_vitals": enabled}})
    return {"enabled_vitals": enabled, "message": f"Vital {'enabled' if req.enabled else 'disabled'}"}

@router.get("/entries")
async def get_entries(request: Request, start_date: str = Query(...), end_date: str = Query(...)):
    user = await get_current_user(request)
    uid = str(user["_id"])
    entries = await db.daily_entries.find(
        {"user_id": uid, "date": {"$gte": start_date, "$lte": end_date}},
        {"_id": 0}
    ).sort("date", 1).to_list(5000)
    return entries

@router.post("/entries")
async def save_entry(entry: EntryData, request: Request):
    user = await get_current_user(request)
    uid = str(user["_id"])
    enabled = user.get("enabled_vitals", [])
    if entry.vital_key not in enabled:
        raise HTTPException(status_code=403, detail="This vital is not enabled")
    doc = {"user_id": uid, "vital_key": entry.vital_key, "date": entry.date, "value": entry.value}
    if entry.value2 is not None:
        doc["value2"] = entry.value2
    if entry.notes:
        doc["notes"] = entry.notes
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.daily_entries.update_one(
        {"user_id": uid, "vital_key": entry.vital_key, "date": entry.date},
        {"$set": doc}, upsert=True
    )
    return {"message": "Entry saved", "entry": doc}

@router.post("/entries/bulk")
async def save_bulk_entries(req: BulkEntryRequest, request: Request):
    user = await get_current_user(request)
    uid = str(user["_id"])
    enabled = user.get("enabled_vitals", [])
    saved = 0
    for entry in req.entries:
        if entry.vital_key not in enabled:
            continue
        doc = {"user_id": uid, "vital_key": entry.vital_key, "date": entry.date, "value": entry.value, "updated_at": datetime.now(timezone.utc).isoformat()}
        if entry.value2 is not None:
            doc["value2"] = entry.value2
        if entry.notes:
            doc["notes"] = entry.notes
        await db.daily_entries.update_one(
            {"user_id": uid, "vital_key": entry.vital_key, "date": entry.date},
            {"$set": doc}, upsert=True
        )
        saved += 1
    return {"message": f"Saved {saved} entries", "saved": saved}

@router.delete("/entries/{date}/{vital_key}")
async def delete_entry(date: str, vital_key: str, request: Request):
    user = await get_current_user(request)
    result = await db.daily_entries.delete_one({"user_id": str(user["_id"]), "date": date, "vital_key": vital_key})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted"}

def _compute_stats(vals):
    """Compute min, max, avg, count from a list of numeric values."""
    if not vals:
        return {"min": None, "max": None, "avg": None, "count": 0}
    return {"min": round(min(vals), 1), "max": round(max(vals), 1), "avg": round(sum(vals) / len(vals), 1), "count": len(vals)}

@router.get("/charts/{vital_key}")
async def get_chart_data(vital_key: str, request: Request, start_date: str = Query(...), end_date: str = Query(...), compare: bool = False):
    user = await get_current_user(request)
    uid = str(user["_id"])
    plan = get_user_plan(user)
    if plan["chart_history_days"] > 0:
        max_start = (datetime.now(timezone.utc) - timedelta(days=plan["chart_history_days"])).strftime("%Y-%m-%d")
        if start_date < max_start:
            start_date = max_start
    entries = await db.daily_entries.find(
        {"user_id": uid, "vital_key": vital_key, "date": {"$gte": start_date, "$lte": end_date}},
        {"_id": 0}
    ).sort("date", 1).to_list(1000)
    vals = [e["value"] for e in entries if e.get("value") is not None]
    stats = _compute_stats(vals)
    # Compute previous period for comparison
    from datetime import date as date_type
    sd = date_type.fromisoformat(start_date)
    ed = date_type.fromisoformat(end_date)
    period_days = (ed - sd).days
    prev_end = (sd - timedelta(days=1)).isoformat()
    prev_start = (sd - timedelta(days=period_days + 1)).isoformat()
    prev_entries = await db.daily_entries.find(
        {"user_id": uid, "vital_key": vital_key, "date": {"$gte": prev_start, "$lte": prev_end}},
        {"_id": 0}
    ).sort("date", 1).to_list(1000)
    prev_vals = [e["value"] for e in prev_entries if e.get("value") is not None]
    prev_stats = _compute_stats(prev_vals)
    # Compute change percent
    change_percent = None
    if prev_stats["avg"] is not None and stats["avg"] is not None and prev_stats["avg"] != 0:
        change_percent = round(((stats["avg"] - prev_stats["avg"]) / prev_stats["avg"]) * 100, 1)
    # Trend
    trend = "stable"
    if len(vals) >= 3:
        recent = vals[-3:]
        if recent[-1] > recent[0] * 1.05:
            trend = "rising"
        elif recent[-1] < recent[0] * 0.95:
            trend = "falling"
    result = {
        "entries": entries, "vital_key": vital_key,
        "stats": stats, "previous_stats": prev_stats,
        "change_percent": change_percent, "trend": trend,
    }
    if compare:
        result["previous_entries"] = prev_entries
    return result

@router.get("/insights")
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
        entries = await db.daily_entries.find(
            {"user_id": uid, "vital_key": vk, "date": {"$gte": week_ago, "$lte": today}},
            {"_id": 0}
        ).sort("date", 1).to_list(100)
        vals = [e["value"] for e in entries if e.get("value") is not None]
        if not vals:
            continue
        avg = sum(vals) / len(vals)
        latest = vals[-1]
        # Previous week for comparison
        prev_entries = await db.daily_entries.find(
            {"user_id": uid, "vital_key": vk, "date": {"$gte": two_weeks_ago, "$lt": week_ago}},
            {"_id": 0}
        ).to_list(100)
        prev_vals = [e["value"] for e in prev_entries if e.get("value") is not None]
        prev_avg = round(sum(prev_vals) / len(prev_vals), 1) if prev_vals else None
        change_percent = None
        if prev_avg and prev_avg != 0:
            change_percent = round(((avg - prev_avg) / prev_avg) * 100, 1)
        status = "normal"
        if latest < vtype.get("normal_min", 0):
            status = "warning" if latest > vtype.get("normal_min", 0) * 0.8 else "critical"
        elif latest > vtype.get("normal_max", 999):
            status = "warning" if latest < vtype.get("normal_max", 999) * 1.2 else "critical"
        trend = "stable"
        if len(vals) >= 3:
            recent = vals[-3:]
            if recent[-1] > recent[0] * 1.05:
                trend = "rising"
            elif recent[-1] < recent[0] * 0.95:
                trend = "falling"
        message = f"{vtype['name']}: Latest {latest} {vtype['unit']}"
        if status != "normal":
            message += f" ({status})"
        insights.append({
            "vital_key": vk, "vital_name": vtype["name"], "status": status,
            "trend": trend, "latest": latest, "average": round(avg, 1),
            "previous_average": prev_avg, "change_percent": change_percent,
            "entry_count": len(vals), "message": message, "unit": vtype["unit"],
            "normal_min": vtype.get("normal_min"), "normal_max": vtype.get("normal_max"),
            "min": round(min(vals), 1), "max": round(max(vals), 1),
        })
    return insights

@router.get("/reminders")
async def get_reminders(request: Request):
    user = await get_current_user(request)
    reminders = await db.reminders.find({"user_id": str(user["_id"])}).to_list(50)
    return [{"id": str(r["_id"]), **{k: v for k, v in r.items() if k != "_id"}} for r in reminders]

@router.post("/reminders")
async def create_reminder(req: ReminderRequest, request: Request):
    user = await get_current_user(request)
    doc = {"user_id": str(user["_id"]), "vital_keys": req.vital_keys, "time": req.time, "frequency": req.frequency, "enabled": req.enabled, "created_at": datetime.now(timezone.utc).isoformat()}
    result = await db.reminders.insert_one(doc)
    return {"id": str(result.inserted_id), "message": "Reminder created"}

@router.put("/reminders/{reminder_id}")
async def update_reminder(reminder_id: str, req: ReminderRequest, request: Request):
    user = await get_current_user(request)
    from bson import ObjectId
    result = await db.reminders.update_one(
        {"_id": ObjectId(reminder_id), "user_id": str(user["_id"])},
        {"$set": {"vital_keys": req.vital_keys, "time": req.time, "frequency": req.frequency, "enabled": req.enabled}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder updated"}

@router.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str, request: Request):
    user = await get_current_user(request)
    from bson import ObjectId
    result = await db.reminders.delete_one({"_id": ObjectId(reminder_id), "user_id": str(user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted"}
