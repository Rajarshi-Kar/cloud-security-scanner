import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.report import ReportFormat


class ReportCreate(BaseModel):
    format: ReportFormat


class ReportRead(BaseModel):
    id: uuid.UUID
    scan_id: uuid.UUID
    format: ReportFormat
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True
