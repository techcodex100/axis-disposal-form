from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
from typing import Optional, List
import os

app = FastAPI(
    title="Axis Disposal Instruction Generator",
    description="Generates PDFs with background layout for Axis Bank's inward remittance form.",
    version="1.0.0"
)

# 🧾 Table entry model
class DisposalTableEntry(BaseModel):
    remitter_name: Optional[str] = ""
    purpose_code: Optional[str] = ""
    dated: Optional[str] = ""
    remarks: Optional[str] = ""

# 📝 Form data model
class AxisDisposalFormData(BaseModel):
    branch_name: Optional[str] = ""
    account_number_100: Optional[str] = ""
    inr_account_percent: Optional[str] = ""
    eefc_account_percent: Optional[str] = ""
    eefc_account_100: Optional[str] = ""
    purpose_code: Optional[str] = ""
    remitter_address: Optional[str] = ""
    currency: Optional[str] = ""
    max_amount: Optional[str] = ""
    registration_number: Optional[str] = ""
    date: Optional[str] = ""
    place: Optional[str] = ""
    applicant_name: Optional[str] = ""
    applicant_address: Optional[str] = ""
    ie_code: Optional[str] = ""
    table_entries: Optional[List[DisposalTableEntry]] = []

@app.get("/")
def root():
    return {"message": "Axis PDF Generator is live. Use POST /generate-axis-disposal-pdf/"}

@app.post("/generate-axis-disposal-pdf/")
def generate_axis_disposal_pdf(data: AxisDisposalFormData):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica", 12)

        # 🔍 Image folder path
        base_path = os.path.join(os.path.dirname(__file__), "static", "axisbank")
        page_paths = [
            os.path.join(base_path, "1.jpeg"),
            os.path.join(base_path, "2.jpeg"),
            os.path.join(base_path, "3.jpeg")
        ]

        # === Page 1 ===
        if os.path.exists(page_paths[0]):
            c.drawImage(ImageReader(page_paths[0]), 0, 0, width=width, height=height)
        else:
            c.drawString(100, 800, "Missing image: 1.jpeg")

        c.drawString(65, 720, data.branch_name)
        c.drawString(380, 380, data.account_number_100)
        c.drawString(420, 482, data.inr_account_percent)
        c.drawString(460, 455, data.eefc_account_percent)
        c.drawString(360, 415, data.eefc_account_100)
        c.drawString(460, 230, data.purpose_code)
        c.drawString(340, 590, data.remitter_address)
        c.drawString(320, 550, data.currency)
        c.drawString(420, 550, data.max_amount)
        c.showPage()

        # === Page 2 ===
        if os.path.exists(page_paths[1]):
            c.drawImage(ImageReader(page_paths[1]), 0, 0, width=width, height=height)
        else:
            c.drawString(100, 800, "Missing image: 2.jpeg")

        c.drawString(342, 390, data.registration_number)
        c.drawString(100, 122, data.date)
        c.drawString(100, 110, data.place)
        c.drawString(380, 83, data.applicant_name)
        c.drawString(380, 70, data.applicant_address)
        c.drawString(380, 57, data.ie_code)
        c.showPage()

        # === Page 3 ===
        if os.path.exists(page_paths[2]):
            c.drawImage(ImageReader(page_paths[2]), 0, 0, width=width, height=height)
        else:
            c.drawString(100, 800, "Missing image: 3.jpeg")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(390, 783, data.table_entries[0].dated if data.table_entries else "")
        c.setFont("Helvetica", 12)

        table_start_y = 740
        row_height = 20

        for idx, entry in enumerate(data.table_entries or []):
            y = table_start_y - idx * row_height
            c.drawString(75, y, entry.remitter_name)
            c.drawString(220, y, entry.purpose_code)
            c.drawString(420, y, entry.remarks)

        c.save()
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=axis_disposal_form.pdf"}
        )

    except Exception as e:
        print("⚠️ PDF generation failed:", str(e))
        raise HTTPException(status_code=500, detail="PDF generation failed")
