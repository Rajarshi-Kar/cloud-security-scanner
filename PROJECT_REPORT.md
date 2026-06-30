# Project Report — Cloud Security Scanner

A production-style platform for scanning Docker images and source repositories for dependency
vulnerabilities, exposed secrets, and security misconfigurations.

## Status

All 8 planned build batches are complete (see README.md "Batch Plan" for the detailed log).

| Batch | Scope | Status |
|---|---|---|
| 1 | Scaffold, Docker Compose, Auth (JWT/bcrypt/RBAC) | Done |
| 2 | Project/Scan/Vulnerability/Report models + API | Done |
| 3 | Repository Scanner (Gitleaks, Semgrep, pip-audit, Safety) via Celery | Done |
| 4 | Docker Scanner (Trivy) | Done |
| 5 | Dashboard aggregations | Done |
| 6 | Reports (PDF/JSON, CVE links) | Done |
| 7 | Frontend buildout | Done |
| 8 | Tests, CI, Nginx prod config, Swagger polish | Done |

## Codebase Statistics

| Metric | Count |
|---|---|
| Backend Python files | 67 |
| Backend lines of code | ~1,894 |
| Frontend TypeScript/TSX files | 23 |
| Frontend lines of code | ~956 |
| Database models | 5 (`User`, `Project`, `Scan`, `Vulnerability`, `Report`) |
| REST API endpoints | 16 |
| React pages | 5 (`Login`, `Dashboard`, `Projects`, `ProjectDetail`, `ScanDetail`) |
| Shared React components | 4 (`Layout`, `NavBar`, `ProtectedRoute`, `SeverityBadge`) |
| Security scanning engines integrated | 5 (Gitleaks, Semgrep, pip-audit, Safety, Trivy) |
| Celery background tasks | 2 (`scan_repository`, `scan_docker_image`) |
| Pytest test files | 3 (auth, projects, scans) |
| Total tracked files in repo | ~116 |

## API Surface

- **Auth** (3): register, login, current user
- **Projects** (4): create, list, get, delete
- **Scans** (5): create (by target), upload (Docker tar), list, get, list vulnerabilities
- **Reports** (3): generate, list, download
- **Dashboard** (1): aggregated summary

## Architecture

```
React Client → FastAPI → Service Layer → Repository Layer → PostgreSQL
                                ↓
                      Celery Worker (Redis broker)
                                ↓
                   Security Scanner Engine (Gitleaks / Semgrep /
                   pip-audit / Safety / Trivy)
```

Layered with the Repository pattern (`app/repositories/`), Service pattern
(`app/services/`), and dependency injection via FastAPI's `Depends`. RBAC enforced
through a `require_role()` dependency; project/scan/report ownership checks
cascade through each service layer.

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, React Query, React Router, TailwindCSS, Axios, Recharts |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| Database | PostgreSQL |
| Auth | JWT, bcrypt |
| Background jobs | Celery, Redis |
| Scanning | Trivy, Semgrep, Gitleaks, Safety, pip-audit |
| Infra | Docker, Docker Compose, Nginx |
| Dev tools | Git, GitHub, Swagger, Pytest |
| CI/CD | GitHub Actions |

## Not Yet Built (Stretch Goals)

GitHub OAuth, scheduled scans, email alerts, GitHub Actions integration *into scans*,
multi-project workspaces.

---
*Generated 2026-06-30.*
