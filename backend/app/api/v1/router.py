from fastapi import APIRouter

from app.api.v1 import auth, dashboard, projects, reports, scans

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(scans.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)
