import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  -- registers all model metadata before create_all
from app.db.base import Base
from app.db.session import get_db
from app.main import app

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.create_all(_engine)
    yield
    Base.metadata.drop_all(_engine)


@pytest.fixture(autouse=True)
def _no_celery(monkeypatch):
    # Tests never need real scans to run; just verify enqueueing happens without hitting Redis.
    from app.workers import tasks

    monkeypatch.setattr(tasks.scan_repository_task, "delay", lambda *a, **k: None)
    monkeypatch.setattr(tasks.scan_docker_image_task, "delay", lambda *a, **k: None)


@pytest.fixture
def client():
    def override_get_db():
        db = _TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, email: str = "user@example.com", password: str = "Sup3rSecret!") -> str:
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": "Test User"})
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
