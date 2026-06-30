import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.scan import Scan
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanRead
from app.schemas.vulnerability import VulnerabilityRead
from app.services.scan_service import ScanService

router = APIRouter(tags=["scans"])


@router.post("/projects/{project_id}/scans", response_model=ScanRead, status_code=201)
def create_scan(
    project_id: uuid.UUID,
    payload: ScanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Scan:
    return ScanService(db).create(project_id, payload, user)


@router.post("/projects/{project_id}/scans/docker-image", response_model=ScanRead, status_code=201)
def upload_docker_image_scan(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Scan:
    return ScanService(db).create_docker_image_upload(project_id, file, user)


@router.get("/projects/{project_id}/scans", response_model=list[ScanRead])
def list_scans(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Scan]:
    return ScanService(db).list_for_project(project_id, user)


@router.get("/scans/{scan_id}", response_model=ScanRead)
def get_scan(
    scan_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Scan:
    return ScanService(db).get(scan_id, user)


@router.get("/scans/{scan_id}/vulnerabilities", response_model=list[VulnerabilityRead])
def list_scan_vulnerabilities(
    scan_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list:
    return ScanService(db).list_vulnerabilities(scan_id, user)
