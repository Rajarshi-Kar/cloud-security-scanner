import json
import os
import subprocess

from app.core.logging import get_logger
from app.models.vulnerability import Severity, VulnerabilitySource
from app.scanner.findings import Finding

logger = get_logger(__name__)

_TRIVY_SEVERITY_MAP = {
    "CRITICAL": Severity.CRITICAL,
    "HIGH": Severity.HIGH,
    "MEDIUM": Severity.MEDIUM,
    "LOW": Severity.LOW,
    "UNKNOWN": Severity.INFO,
}


def run_trivy(target: str, is_local_tar: bool) -> list[Finding]:
    """Runs trivy against a registry image reference or a local `docker save` tarball."""
    command = ["trivy", "image", "--format", "json", "--quiet"]
    if is_local_tar:
        command += ["--input", target]
    else:
        command += [target]

    try:
        proc = subprocess.run(command, capture_output=True, timeout=900, text=True)
    except FileNotFoundError as exc:
        logger.warning("trivy run failed: %s", exc)
        return []

    if not proc.stdout:
        logger.warning("trivy produced no output for %s: %s", target, proc.stderr)
        return []

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        logger.warning("trivy produced non-JSON output for %s", target)
        return []

    findings: list[Finding] = []
    for result in payload.get("Results", []):
        target_name = result.get("Target")
        for vuln in result.get("Vulnerabilities", []) or []:
            severity = _TRIVY_SEVERITY_MAP.get(vuln.get("Severity", "UNKNOWN"), Severity.INFO)
            findings.append(
                Finding(
                    source=VulnerabilitySource.TRIVY,
                    severity=severity,
                    title=vuln.get("Title") or f"{vuln.get('VulnerabilityID')} in {vuln.get('PkgName')}",
                    description=vuln.get("Description"),
                    cve_id=vuln.get("VulnerabilityID"),
                    package_name=(
                        f"{vuln.get('PkgName')}=={vuln.get('InstalledVersion')}"
                        if vuln.get("PkgName")
                        else None
                    ),
                    file_path=target_name,
                )
            )
    return findings


def cleanup_tar(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)
