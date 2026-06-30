import uuid
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.scan import Scan, ScanStatus
from app.models.vulnerability import Severity, Vulnerability


class DashboardRepository:
    """Aggregation queries scoped to a single owner's projects, or all projects when owner_id is None (admin)."""

    def __init__(self, db: Session):
        self.db = db

    def _scan_query(self, owner_id: uuid.UUID | None):
        query = self.db.query(Scan).join(Project, Scan.project_id == Project.id)
        if owner_id is not None:
            query = query.filter(Project.owner_id == owner_id)
        return query

    def _vulnerability_query(self, owner_id: uuid.UUID | None):
        query = (
            self.db.query(Vulnerability)
            .join(Scan, Vulnerability.scan_id == Scan.id)
            .join(Project, Scan.project_id == Project.id)
        )
        if owner_id is not None:
            query = query.filter(Project.owner_id == owner_id)
        return query

    def count_projects(self, owner_id: uuid.UUID | None) -> int:
        query = self.db.query(Project)
        if owner_id is not None:
            query = query.filter(Project.owner_id == owner_id)
        return query.count()

    def count_scans(self, owner_id: uuid.UUID | None) -> int:
        return self._scan_query(owner_id).count()

    def average_security_score(self, owner_id: uuid.UUID | None) -> float | None:
        result = (
            self._scan_query(owner_id)
            .filter(Scan.status == ScanStatus.COMPLETED, Scan.security_score.isnot(None))
            .with_entities(func.avg(Scan.security_score))
            .scalar()
        )
        return round(float(result), 1) if result is not None else None

    def severity_breakdown(self, owner_id: uuid.UUID | None) -> dict[Severity, int]:
        rows = (
            self._vulnerability_query(owner_id)
            .with_entities(Vulnerability.severity, func.count(Vulnerability.id))
            .group_by(Vulnerability.severity)
            .all()
        )
        return dict(rows)

    def recent_scans(self, owner_id: uuid.UUID | None, limit: int = 5) -> list[Scan]:
        return self._scan_query(owner_id).order_by(Scan.created_at.desc()).limit(limit).all()

    def critical_issues(self, owner_id: uuid.UUID | None, limit: int = 10) -> list[Vulnerability]:
        return (
            self._vulnerability_query(owner_id)
            .filter(Vulnerability.severity.in_([Severity.CRITICAL, Severity.HIGH]))
            .order_by(Vulnerability.created_at.desc())
            .limit(limit)
            .all()
        )

    def vulnerability_trend(self, owner_id: uuid.UUID | None, days: int = 14) -> list[tuple[str, int]]:
        since = datetime.utcnow() - timedelta(days=days)
        rows = (
            self._vulnerability_query(owner_id)
            .filter(Vulnerability.created_at >= since)
            .with_entities(func.date(Vulnerability.created_at), func.count(Vulnerability.id))
            .group_by(func.date(Vulnerability.created_at))
            .order_by(func.date(Vulnerability.created_at))
            .all()
        )
        return [(str(date), count) for date, count in rows]
