import os
from fastapi import APIRouter, Depends, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.cti.report_generator import generate_executive_soc_report

router = APIRouter(prefix="/reports", tags=["Reports & Export"])

@router.get("/executive")
def get_executive_report(db: Session = Depends(get_db)):
    md = generate_executive_soc_report(db)
    return {"report_markdown": md}

@router.get("/download")
def download_executive_report(db: Session = Depends(get_db)):
    md = generate_executive_soc_report(db)
    response = Response(content=md, media_type="text/markdown")
    response.headers["Content-Disposition"] = "attachment; filename=soc_executive_threat_report.md"
    return response

@router.get("/pdf")
def download_pdf_report():
    possible_paths = [
        os.path.abspath("Project_Architecture_and_Implementation_Report.pdf"),
        os.path.abspath(os.path.join("docs", "Project_Architecture_and_Implementation_Report.pdf")),
        os.path.abspath(os.path.join("..", "Project_Architecture_and_Implementation_Report.pdf")),
        os.path.abspath(os.path.join("..", "docs", "Project_Architecture_and_Implementation_Report.pdf"))
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return FileResponse(
                p,
                media_type="application/pdf",
                filename="Project_Architecture_and_Implementation_Report.pdf"
            )
    return Response(content="PDF report not found on server", status_code=404)

