import os
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.scan import Scan, ScanType
from app.models.user import User
from app.repositories.scan_repository import ScanRepository
from app.repositories.vulnerability_repository import VulnerabilityRepository
from app.schemas.scan import ScanCreate
from app.services.project_service import ProjectService

_ALLOWED_IMAGE_EXTENSIONS = (".tar",)


class ScanService:
    def __init__(self, db: Session):
        self.repo = ScanRepository(db)
        self.vuln_repo = VulnerabilityRepository(db)
        self.project_service = ProjectService(db)

    def create(self, project_id: uuid.UUID, payload: ScanCreate, user: User) -> Scan:
        # Ensures the caller owns (or admins) the parent project before queuing a scan.
        self.project_service.get_owned(project_id, user)
        scan = Scan(project_id=project_id, scan_type=payload.scan_type, target=payload.target)
        scan = self.repo.create(scan)

        if scan.scan_type == ScanType.REPOSITORY:
            # Local import: keeps Celery/scanner deps out of the request-handling import path.
            from app.workers.tasks import scan_repository_task

            scan_repository_task.delay(str(scan.id))
        elif scan.scan_type == ScanType.DOCKER_IMAGE:
            from app.workers.tasks import scan_docker_image_task

            scan_docker_image_task.delay(str(scan.id), False)

        return scan

    def create_docker_image_upload(self, project_id: uuid.UUID, file: UploadFile, user: User) -> Scan:
        self.project_service.get_owned(project_id, user)
        if not file.filename or not file.filename.endswith(_ALLOWED_IMAGE_EXTENSIONS):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Upload a `docker save` .tar archive")

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        dest_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}.tar")
        with open(dest_path, "wb") as f:
            while chunk := file.file.read(1024 * 1024):
                f.write(chunk)

        scan = Scan(project_id=project_id, scan_type=ScanType.DOCKER_IMAGE, target=dest_path)
        scan = self.repo.create(scan)

        from app.workers.tasks import scan_docker_image_task

        scan_docker_image_task.delay(str(scan.id), True)
        return scan

    def list_for_project(self, project_id: uuid.UUID, user: User) -> list[Scan]:
        self.project_service.get_owned(project_id, user)
        return self.repo.list_for_project(project_id)

    def get(self, scan_id: uuid.UUID, user: User) -> Scan:
        scan = self.repo.get(scan_id)
        if not scan:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Scan not found")
        self.project_service.get_owned(scan.project_id, user)
        return scan

    def list_vulnerabilities(self, scan_id: uuid.UUID, user: User) -> list:
        scan = self.get(scan_id, user)
        return self.vuln_repo.list_for_scan(scan.id)
