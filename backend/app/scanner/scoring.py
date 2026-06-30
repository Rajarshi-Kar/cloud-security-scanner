from app.models.vulnerability import Severity
from app.scanner.findings import Finding

_SEVERITY_WEIGHT = {
    Severity.CRITICAL: 25,
    Severity.HIGH: 15,
    Severity.MEDIUM: 7,
    Severity.LOW: 3,
    Severity.INFO: 1,
}


def compute_security_score(findings: list[Finding]) -> int:
    penalty = sum(_SEVERITY_WEIGHT[f.severity] for f in findings)
    return max(0, 100 - penalty)
