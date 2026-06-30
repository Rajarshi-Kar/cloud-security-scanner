from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

_TAGS_METADATA = [
    {"name": "auth", "description": "Registration, login, and the current-user JWT identity."},
    {"name": "projects", "description": "Projects owned by a user; the scope every scan belongs to."},
    {"name": "scans", "description": "Repository (Gitleaks/Semgrep/pip-audit/Safety) and Docker image (Trivy) scans."},
    {"name": "reports", "description": "PDF/JSON report generation and download for completed scans."},
    {"name": "dashboard", "description": "Aggregated security score, trends, and recent activity."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Scans Docker images and source repositories for vulnerabilities, secrets, and misconfigurations.",
    version="0.1.0",
    openapi_tags=_TAGS_METADATA,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
