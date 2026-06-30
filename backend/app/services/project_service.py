import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User, UserRole
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

    def create(self, payload: ProjectCreate, owner: User) -> Project:
        project = Project(name=payload.name, repo_url=payload.repo_url, owner_id=owner.id)
        return self.repo.create(project)

    def list_for_user(self, user: User) -> list[Project]:
        if user.role == UserRole.ADMIN:
            return self.repo.list()
        return self.repo.list_for_owner(user.id)

    def get_owned(self, project_id: uuid.UUID, user: User) -> Project:
        project = self.repo.get(project_id)
        if not project:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
        if user.role != UserRole.ADMIN and project.owner_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your project")
        return project

    def delete(self, project_id: uuid.UUID, user: User) -> None:
        project = self.get_owned(project_id, user)
        self.repo.delete(project)
