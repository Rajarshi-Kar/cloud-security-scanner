import json
import subprocess

from app.core.logging import get_logger
from app.models.vulnerability import Severity, VulnerabilitySource
from app.scanner.findings import Finding

logger = get_logger(__name__)

_SEMGREP_SEVERITY_MAP = {
    "ERROR": Severity.HIGH,
    "WARNING": Severity.MEDIUM,
    "INFO": Severity.LOW,
}


def run_semgrep(repo_path: str) -> list[Finding]:
    """Runs semgrep's auto ruleset against the repo and returns one Finding per result."""
    try:
        proc = subprocess.run(
            ["semgrep", "--config=auto", "--json", "--quiet", repo_path],
            capture_output=True,
            timeout=600,
            text=True,
        )
    except FileNotFoundError as exc:
        logger.warning("semgrep run failed: %s", exc)
        return []

    if not proc.stdout:
        return []

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        logger.warning("semgrep produced non-JSON output")
        return []

    findings: list[Finding] = []
    for result in payload.get("results", []):
        extra = result.get("extra", {})
        severity = _SEMGREP_SEVERITY_MAP.get(extra.get("severity", "INFO"), Severity.LOW)
        findings.append(
            Finding(
                source=VulnerabilitySource.SEMGREP,
                severity=severity,
                title=extra.get("message", result.get("check_id", "semgrep finding"))[:255],
                description=result.get("check_id"),
                file_path=result.get("path"),
            )
        )
    return findings
