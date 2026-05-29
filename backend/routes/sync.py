from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone

from config import db
from utils import get_current_user

router = APIRouter()

@router.post("/sync/register-device")
async def register_device(request: Request):
    """Register a device for sync. Stores device metadata and last sync timestamp."""
    user = await get_current_user(request)
    body = await request.json()
    device_id = body.get("device_id")
    device_type = body.get("device_type", "unknown")
    device_name = body.get("device_name", "")
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id is required")
    uid = str(user["_id"])
    now = datetime.now(timezone.utc).isoformat()
    await db.devices.update_one(
        {"user_id": uid, "device_id": device_id},
        {"$set": {
            "user_id": uid, "device_id": device_id, "device_type": device_type,
            "device_name": device_name, "last_seen": now, "registered_at": now
        }},
        upsert=True
    )
    return {"message": "Device registered", "device_id": device_id}

@router.get("/sync/devices")
async def list_devices(request: Request):
    """List all registered devices for the current user."""
    user = await get_current_user(request)
    devices = await db.devices.find(
        {"user_id": str(user["_id"])}, {"_id": 0}
    ).to_list(20)
    return {"devices": devices}

@router.delete("/sync/devices/{device_id}")
async def remove_device(device_id: str, request: Request):
    """Remove a registered device."""
    user = await get_current_user(request)
    result = await db.devices.delete_one({"user_id": str(user["_id"]), "device_id": device_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device removed"}

@router.get("/sync/pull")
async def sync_pull(request: Request, since: str = ""):
    """
    Pull changes since a given timestamp (ISO format).
    Returns all entries/settings modified after that timestamp.
    If `since` is empty, returns all data (full sync).
    """
    user = await get_current_user(request)
    uid = str(user["_id"])

    entry_query = {"user_id": uid}
    if since:
        entry_query["updated_at"] = {"$gt": since}

    entries = await db.daily_entries.find(
        entry_query, {"_id": 0}
    ).sort("updated_at", 1).to_list(10000)

    # Also return user settings/enabled vitals for sync
    user_data = {
        "enabled_vitals": user.get("enabled_vitals", []),
        "plan": user.get("plan", "free"),
        "name": user.get("name", ""),
        "settings": user.get("settings", {}),
    }

    now = datetime.now(timezone.utc).isoformat()
    return {
        "entries": entries,
        "user_data": user_data,
        "sync_timestamp": now,
        "entry_count": len(entries)
    }

@router.post("/sync/push")
async def sync_push(request: Request):
    """
    Push entries from device to server.
    Uses upsert: if entry already exists for (user, vital_key, date), update it.
    Accepts: { entries: [...], device_id: "..." }
    """
    user = await get_current_user(request)
    uid = str(user["_id"])
    body = await request.json()
    entries = body.get("entries", [])
    device_id = body.get("device_id", "")

    enabled = user.get("enabled_vitals", [])
    synced = 0
    skipped = 0

    for entry in entries:
        vk = entry.get("vital_key")
        date = entry.get("date")
        value = entry.get("value")
        if not vk or not date or value is None:
            skipped += 1
            continue
        if vk not in enabled:
            skipped += 1
            continue
        doc = {
            "user_id": uid, "vital_key": vk, "date": date, "value": value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        if entry.get("value2") is not None:
            doc["value2"] = entry["value2"]
        if entry.get("notes"):
            doc["notes"] = entry["notes"]
        if device_id:
            doc["source_device"] = device_id
        await db.daily_entries.update_one(
            {"user_id": uid, "vital_key": vk, "date": date},
            {"$set": doc}, upsert=True
        )
        synced += 1

    # Update device last_seen
    if device_id:
        await db.devices.update_one(
            {"user_id": uid, "device_id": device_id},
            {"$set": {"last_seen": datetime.now(timezone.utc).isoformat()}}
        )

    return {"message": f"Synced {synced} entries", "synced": synced, "skipped": skipped}
