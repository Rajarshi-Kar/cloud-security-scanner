import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.scan import ScanStatus, ScanType


class ScanCreate(BaseModel):
    scan_type: ScanType
    target: str


class ScanRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    scan_type: ScanType
    status: ScanStatus
    target: str
    security_score: int | None
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True
