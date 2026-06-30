import glob
import json
import os
import subprocess

from app.core.logging import get_logger
from app.models.vulnerability import Severity, VulnerabilitySource
from app.scanner.findings import Finding

logger = get_logger(__name__)


def _find_requirements_files(repo_path: str) -> list[str]:
    return glob.glob(os.path.join(repo_path, "**", "requirements*.txt"), recursive=True)


def run_pip_audit(repo_path: str) -> list[Finding]:
    """Runs pip-audit against each requirements*.txt found in the repo."""
    findings: list[Finding] = []
    for req_file in _find_requirements_files(repo_path):
        try:
            proc = subprocess.run(
                ["pip-audit", "-r", req_file, "-f", "json", "--progress-spinner", "off"],
                capture_output=True,
                timeout=300,
                text=True,
            )
        except FileNotFoundError as exc:
            logger.warning("pip-audit run failed: %s", exc)
            return findings

        if not proc.stdout:
            continue
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            continue

        for dep in payload.get("dependencies", []):
            for vuln in dep.get("vulns", []):
                findings.append(
                    Finding(
                        source=VulnerabilitySource.PIP_AUDIT,
                        severity=Severity.HIGH,
                        title=f"Vulnerable package: {dep.get('name')}=={dep.get('version')}",
                        description=vuln.get("description"),
                        cve_id=next((a for a in vuln.get("aliases", []) if a.startswith("CVE-")), None),
                        package_name=dep.get("name"),
                        file_path=os.path.relpath(req_file, repo_path),
                    )
                )
    return findings


def run_safety(repo_path: str) -> list[Finding]:
    """Runs safety against each requirements*.txt found in the repo."""
    findings: list[Finding] = []
    for req_file in _find_requirements_files(repo_path):
        try:
            proc = subprocess.run(
                ["safety", "check", "-r", req_file, "--json"],
                capture_output=True,
                timeout=300,
                text=True,
            )
        except FileNotFoundError as exc:
            logger.warning("safety run failed: %s", exc)
            return findings

        if not proc.stdout:
            continue
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            continue

        for vuln in payload.get("vulnerabilities", []):
            findings.append(
                Finding(
                    source=VulnerabilitySource.SAFETY,
                    severity=Severity.MEDIUM,
                    title=f"Vulnerable package: {vuln.get('package_name')}=={vuln.get('analyzed_version')}",
                    description=vuln.get("advisory"),
                    cve_id=vuln.get("CVE"),
                    package_name=vuln.get("package_name"),
                    file_path=os.path.relpath(req_file, repo_path),
                )
            )
    return findings
