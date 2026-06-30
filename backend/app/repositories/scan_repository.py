import uuid

from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.repositories.base import BaseRepository


class ScanRepository(BaseRepository[Scan]):
    def __init__(self, db: Session):
        super().__init__(Scan, db)

    def list_for_project(self, project_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Scan]:
        return list(
            self.db.query(Scan)
            .filter(Scan.project_id == project_id)
            .order_by(Scan.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
