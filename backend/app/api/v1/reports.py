import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.report import Report
from app.models.user import User
from app.schemas.report import ReportCreate, ReportRead
from app.services.report_service import ReportService

router = APIRouter(tags=["reports"])


@router.post("/scans/{scan_id}/reports", response_model=ReportRead, status_code=201)
def create_report(
    scan_id: uuid.UUID,
    payload: ReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Report:
    return ReportService(db).generate(scan_id, payload.format, user)


@router.get("/scans/{scan_id}/reports", response_model=list[ReportRead])
def list_reports(
    scan_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[Report]:
    return ReportService(db).list_for_scan(scan_id, user)


@router.get("/reports/{report_id}/download")
def download_report(
    report_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> FileResponse:
    report = ReportService(db).get_owned(report_id, user)
    media_type = "application/pdf" if report.format.value == "pdf" else "application/json"
    filename = f"scan-report-{report.scan_id}.{report.format.value}"
    return FileResponse(report.file_path, media_type=media_type, filename=filename)
