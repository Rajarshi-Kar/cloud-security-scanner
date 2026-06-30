from pydantic import BaseModel

from app.schemas.scan import ScanRead
from app.schemas.vulnerability import VulnerabilityRead


class SeverityBreakdown(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class TrendPoint(BaseModel):
    date: str
    vulnerability_count: int


class DashboardSummary(BaseModel):
    overall_security_score: float | None
    total_projects: int
    total_scans: int
    severity_breakdown: SeverityBreakdown
    recent_scans: list[ScanRead]
    critical_issues: list[VulnerabilityRead]
    trend: list[TrendPoint]
