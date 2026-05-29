from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
import io
import csv

from config import db, VITAL_TYPES
from models import ExportRequest
from utils import get_current_user, get_user_plan

router = APIRouter()

@router.post("/exports/generate")
async def generate_export(req: ExportRequest, request: Request):
    user = await get_current_user(request)
    plan = get_user_plan(user)
    if req.format == "pdf" and not plan["pdf_export"]:
        raise HTTPException(status_code=403, detail="PDF export requires Standard or Premium plan")
    uid = str(user["_id"])
    entries = await db.daily_entries.find(
        {"user_id": uid, "vital_key": {"$in": req.vital_keys}, "date": {"$gte": req.start_date, "$lte": req.end_date}},
        {"_id": 0}
    ).sort("date", 1).to_list(10000)
    if req.format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Vital", "Value", "Value2", "Unit", "Notes"])
        for e in entries:
            vtype = next((v for v in VITAL_TYPES if v["key"] == e["vital_key"]), {})
            writer.writerow([e["date"], vtype.get("name", e["vital_key"]), e.get("value", ""), e.get("value2", ""), vtype.get("unit", ""), e.get("notes", "")])
        writer.writerow([])
        writer.writerow(["--- Summary Statistics ---"])
        for vk in req.vital_keys:
            vtype = next((v for v in VITAL_TYPES if v["key"] == vk), {})
            vals = [e["value"] for e in entries if e["vital_key"] == vk and e.get("value") is not None]
            if vals:
                writer.writerow([vtype.get("name", vk), f"Min: {min(vals)}", f"Max: {max(vals)}", f"Avg: {round(sum(vals)/len(vals), 1)}", f"Count: {len(vals)}"])
        output.seek(0)
        await db.exports.insert_one({"user_id": uid, "type": "csv", "vital_keys": req.vital_keys, "start_date": req.start_date, "end_date": req.end_date, "entry_count": len(entries), "created_at": datetime.now(timezone.utc).isoformat()})
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=vitals_{req.start_date}_{req.end_date}.csv"}
        )
    elif req.format == "pdf":
        from fpdf import FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        pdf.set_fill_color(14, 165, 233)
        pdf.rect(0, 0, 210, 35, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_y(8)
        pdf.cell(0, 10, "VitalTrack Health Report", ln=True, align="C")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"{user.get('name', 'User')} | {req.start_date} to {req.end_date} | Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(8)
        if plan["key"] == "free":
            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(180, 180, 180)
            pdf.cell(0, 5, "FREE PLAN - Upgrade for full reports without watermark", ln=True, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(248, 250, 252)
        col_w = [24, 38, 24, 24, 18, 62]
        headers_row = ["Date", "Vital", "Value", "Value2", "Unit", "Notes"]
        for i, h in enumerate(headers_row):
            pdf.cell(col_w[i], 8, h, border=1, align="C", fill=True)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for e in entries:
            vtype = next((v for v in VITAL_TYPES if v["key"] == e["vital_key"]), {})
            row = [e["date"], vtype.get("name", e["vital_key"])[:20], str(e.get("value", "")), str(e.get("value2", "")), vtype.get("unit", ""), (e.get("notes", "") or "")[:32]]
            for i, val in enumerate(row):
                pdf.cell(col_w[i], 6, val, border=1)
            pdf.ln()
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(14, 165, 233)
        pdf.cell(0, 8, "Summary Statistics", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(248, 250, 252)
        for h_text, w in [("Vital", 50), ("Min", 25), ("Max", 25), ("Average", 30), ("Entries", 25)]:
            pdf.cell(w, 7, h_text, border=1, align="C", fill=True)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for vk in req.vital_keys:
            vtype = next((v for v in VITAL_TYPES if v["key"] == vk), {})
            vals = [e["value"] for e in entries if e["vital_key"] == vk and e.get("value") is not None]
            if vals:
                row_data = [vtype.get("name", vk)[:26], str(round(min(vals), 1)), str(round(max(vals), 1)), str(round(sum(vals)/len(vals), 1)), str(len(vals))]
                for val, w in zip(row_data, [50, 25, 25, 30, 25]):
                    pdf.cell(w, 6, val, border=1, align="C")
                pdf.ln()
        if plan["key"] == "free":
            pdf.set_y(-30)
            pdf.set_font("Helvetica", "B", 28)
            pdf.set_text_color(230, 230, 230)
            pdf.cell(0, 10, "VITALTRACK FREE", align="C")
        buf = io.BytesIO()
        pdf.output(buf)
        buf.seek(0)
        await db.exports.insert_one({"user_id": uid, "type": "pdf", "vital_keys": req.vital_keys, "start_date": req.start_date, "end_date": req.end_date, "entry_count": len(entries), "created_at": datetime.now(timezone.utc).isoformat()})
        return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=vitals_{req.start_date}_{req.end_date}.pdf"})
    raise HTTPException(status_code=400, detail="Invalid format")

@router.get("/exports")
async def list_exports(request: Request):
    user = await get_current_user(request)
    exports = await db.exports.find({"user_id": str(user["_id"])}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return exports
