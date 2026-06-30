import uuid
from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    repo_url: str | None = None


class ProjectRead(BaseModel):
    id: uuid.UUID
    name: str
    repo_url: str | None
    owner_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
