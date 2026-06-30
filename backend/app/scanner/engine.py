from dataclasses import dataclass

from app.scanner.dependency_scanner import run_pip_audit, run_safety
from app.scanner.findings import Finding
from app.scanner.sast_scanner import run_semgrep
from app.scanner.scoring import compute_security_score
from app.scanner.secret_scanner import run_gitleaks
from app.scanner.workspace import cloned_repository


@dataclass
class RepositoryScanResult:
    findings: list[Finding]
    security_score: int


def run_repository_scan(repo_url: str) -> RepositoryScanResult:
    with cloned_repository(repo_url) as repo_path:
        findings = [
            *run_gitleaks(repo_path),
            *run_semgrep(repo_path),
            *run_pip_audit(repo_path),
            *run_safety(repo_path),
        ]
    return RepositoryScanResult(findings=findings, security_score=compute_security_score(findings))
