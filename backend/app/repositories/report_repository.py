import uuid

from sqlalchemy.orm import Session

from app.models.report import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    def __init__(self, db: Session):
        super().__init__(Report, db)

    def list_for_scan(self, scan_id: uuid.UUID) -> list[Report]:
        return (
            self.db.query(Report)
            .filter(Report.scan_id == scan_id)
            .order_by(Report.created_at.desc())
            .all()
        )
