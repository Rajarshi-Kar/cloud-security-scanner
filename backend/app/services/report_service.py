import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.report import Report, ReportFormat
from app.models.scan import ScanStatus
from app.models.user import User
from app.repositories.report_repository import ReportRepository
from app.reporting.json_report import generate_json_report
from app.reporting.pdf_report import generate_pdf_report
from app.services.scan_service import ScanService


class ReportService:
    def __init__(self, db: Session):
        self.repo = ReportRepository(db)
        self.scan_service = ScanService(db)

    def generate(self, scan_id: uuid.UUID, report_format: ReportFormat, user: User) -> Report:
        scan = self.scan_service.get(scan_id, user)
        if scan.status != ScanStatus.COMPLETED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Scan must be completed before generating a report")

        vulnerabilities = self.scan_service.list_vulnerabilities(scan_id, user)
        dest_path = f"{settings.REPORTS_DIR}/{scan.id}/{uuid.uuid4()}.{report_format.value}"

        if report_format == ReportFormat.JSON:
            generate_json_report(scan, vulnerabilities, dest_path)
        else:
            generate_pdf_report(scan, vulnerabilities, dest_path)

        report = Report(scan_id=scan.id, format=report_format, file_path=dest_path)
        return self.repo.create(report)

    def list_for_scan(self, scan_id: uuid.UUID, user: User) -> list[Report]:
        self.scan_service.get(scan_id, user)  # ownership check
        return self.repo.list_for_scan(scan_id)

    def get_owned(self, report_id: uuid.UUID, user: User) -> Report:
        report = self.repo.get(report_id)
        if not report:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found")
        self.scan_service.get(report.scan_id, user)  # ownership check
        return report
