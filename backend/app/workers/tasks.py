import uuid
from collections.abc import Callable
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.scan import Scan, ScanStatus
from app.models.vulnerability import Vulnerability
from app.repositories.scan_repository import ScanRepository
from app.scanner.docker_engine import run_docker_scan
from app.scanner.engine import run_repository_scan
from app.scanner.findings import Finding
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


def _persist_scan_result(db: Session, scan: Scan, findings: list[Finding], security_score: int) -> None:
    for finding in findings:
        db.add(
            Vulnerability(
                scan_id=scan.id,
                source=finding.source,
                severity=finding.severity,
                title=finding.title,
                description=finding.description,
                cve_id=finding.cve_id,
                package_name=finding.package_name,
                file_path=finding.file_path,
            )
        )
    scan.status = ScanStatus.COMPLETED
    scan.security_score = security_score
    scan.completed_at = datetime.utcnow()
    db.commit()


def _run_scan(scan_id: str, run: Callable[[Scan], tuple[list[Finding], int]]) -> None:
    db = SessionLocal()
    try:
        repo = ScanRepository(db)
        scan = repo.get(uuid.UUID(scan_id))
        if not scan:
            logger.warning("scan %s not found, skipping", scan_id)
            return

        scan.status = ScanStatus.RUNNING
        db.commit()

        try:
            findings, security_score = run(scan)
        except Exception:
            logger.exception("scan failed for scan %s", scan_id)
            scan.status = ScanStatus.FAILED
            scan.completed_at = datetime.utcnow()
            db.commit()
            return

        _persist_scan_result(db, scan, findings, security_score)
    finally:
        db.close()


@celery_app.task(name="scan_repository")
def scan_repository_task(scan_id: str) -> None:
    def run(scan: Scan) -> tuple[list[Finding], int]:
        result = run_repository_scan(scan.target)
        return result.findings, result.security_score

    _run_scan(scan_id, run)


@celery_app.task(name="scan_docker_image")
def scan_docker_image_task(scan_id: str, is_local_tar: bool) -> None:
    def run(scan: Scan) -> tuple[list[Finding], int]:
        result = run_docker_scan(scan.target, is_local_tar=is_local_tar)
        return result.findings, result.security_score

    _run_scan(scan_id, run)
