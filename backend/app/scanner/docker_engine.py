from dataclasses import dataclass

from app.scanner.findings import Finding
from app.scanner.image_scanner import cleanup_tar, run_trivy
from app.scanner.scoring import compute_security_score


@dataclass
class DockerScanResult:
    findings: list[Finding]
    security_score: int


def run_docker_scan(target: str, is_local_tar: bool) -> DockerScanResult:
    try:
        findings = run_trivy(target, is_local_tar=is_local_tar)
    finally:
        if is_local_tar:
            cleanup_tar(target)
    return DockerScanResult(findings=findings, security_score=compute_security_score(findings))
