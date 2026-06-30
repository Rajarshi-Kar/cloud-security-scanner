from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardSummary, SeverityBreakdown, TrendPoint


class DashboardService:
    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_summary(self, user: User) -> DashboardSummary:
        owner_id = None if user.role == UserRole.ADMIN else user.id

        breakdown = self.repo.severity_breakdown(owner_id)
        severity = SeverityBreakdown(
            **{sev.value: count for sev, count in breakdown.items()}
        )

        return DashboardSummary(
            overall_security_score=self.repo.average_security_score(owner_id),
            total_projects=self.repo.count_projects(owner_id),
            total_scans=self.repo.count_scans(owner_id),
            severity_breakdown=severity,
            recent_scans=self.repo.recent_scans(owner_id),
            critical_issues=self.repo.critical_issues(owner_id),
            trend=[
                TrendPoint(date=date, vulnerability_count=count)
                for date, count in self.repo.vulnerability_trend(owner_id)
            ],
        )
