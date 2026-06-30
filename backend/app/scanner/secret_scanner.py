import json
import os
import subprocess
import tempfile

from app.core.logging import get_logger
from app.models.vulnerability import Severity, VulnerabilitySource
from app.scanner.findings import Finding

logger = get_logger(__name__)


def run_gitleaks(repo_path: str) -> list[Finding]:
    """Runs gitleaks against the working tree and returns one Finding per leaked secret."""
    report_path = os.path.join(tempfile.mkdtemp(prefix="gitleaks-"), "report.json")
    try:
        subprocess.run(
            [
                "gitleaks",
                "detect",
                "--source",
                repo_path,
                "--no-git",
                "--report-format",
                "json",
                "--report-path",
                report_path,
                "--exit-code",
                "0",
            ],
            check=True,
            capture_output=True,
            timeout=300,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logger.warning("gitleaks run failed: %s", exc)
        return []

    if not os.path.exists(report_path) or os.path.getsize(report_path) == 0:
        return []

    with open(report_path, encoding="utf-8") as f:
        results = json.load(f)

    return [
        Finding(
            source=VulnerabilitySource.GITLEAKS,
            severity=Severity.HIGH,
            title=f"Secret detected: {item.get('RuleID', 'unknown-rule')}",
            description=item.get("Description"),
            file_path=item.get("File"),
        )
        for item in results
    ]
