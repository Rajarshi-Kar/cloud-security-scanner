# Cloud Security Scanner

Production-style platform for scanning Docker images and source repositories for vulnerabilities, secrets, and misconfigurations.

See [PROJECT_REPORT.md](PROJECT_REPORT.md) for codebase statistics, the full tech stack, and API surface.

> `claude.md`, `design.md`, and `tech_stack.md` were this project's internal planning docs (used
> to drive the AI-assisted build). They're listed in `.gitignore` and not part of the pushed repo.

## Batch Plan

- [x] **Batch 1** — Repo scaffold, Docker Compose, Auth (JWT + bcrypt + RBAC), DB/Repository/Service layers
- [x] **Batch 2** — Project/Scan/Vulnerability/Report models + Projects/Scans API
- [x] **Batch 3** — Repository Scanner: clone repo, Gitleaks (secrets), Semgrep + pip-audit/Safety (deps), Celery worker
- [x] **Batch 4** — Docker Scanner: image upload, Trivy layer/vuln analysis
- [x] **Batch 5** — Dashboard aggregations: security score, trends, recent scans, critical issues
- [x] **Batch 6** — Reports: PDF/JSON export, CVE links
- [x] **Batch 7** — Frontend buildout: scan upload UI, results tables, dashboard charts (Recharts), search/filter
- [x] **Batch 8** — Tests (Pytest), CI (GitHub Actions), Nginx deploy config, Swagger polish

## Running Batch 1

```
cp backend/.env.example backend/.env   # edit JWT_SECRET_KEY
docker compose -f docker/docker-compose.yml up --build
```

- Backend: http://localhost:8000/docs
- Frontend: http://localhost:5173
- `POST /api/v1/auth/register` then `/auth/login` to get a JWT, `/auth/me` to verify RBAC role claim.

## Batch 2 notes

New entities: `Project` (owned by a user), `Scan` (repository or docker_image type, status lifecycle
pending->running->completed/failed), `Vulnerability` (severity/source/CVE), `Report` (pdf/json, added now
for the schema but not yet generated — that's Batch 6).

New endpoints: `POST/GET /projects`, `GET/DELETE /projects/{id}`, `POST/GET /projects/{id}/scans`,
`GET /scans/{id}`, `GET /scans/{id}/vulnerabilities`. Ownership enforced in `ProjectService.get_owned` —
non-admins can only see their own projects. Creating a scan only inserts a `pending` row; the Celery
worker that actually runs Gitleaks/Semgrep/Trivy against it lands in Batch 3/4.

## Batch 3 notes

`POST /projects/{id}/scans` with `scan_type: "repository"` now does real work: it enqueues
`scan_repository_task` on a new `worker` container (Celery + Redis). The task shallow-clones the
repo into a temp dir, runs Gitleaks (secrets), Semgrep `--config=auto` (SAST), and pip-audit +
Safety against any `requirements*.txt` it finds, converts results into `Vulnerability` rows, sets
`Scan.status` to `completed`/`failed`, and computes `security_score` (100 minus a per-severity
penalty). Poll `GET /scans/{id}` for status and `GET /scans/{id}/vulnerabilities` for results.

Engine code lives in `backend/app/scanner/` (one module per tool + `engine.py` to orchestrate);
Celery wiring is in `backend/app/workers/`. Tools are invoked as subprocesses — `gitleaks` is
installed as a binary in the Docker image, `semgrep`/`pip-audit`/`safety` are pip packages. Docker
image scanning (Trivy) and its worker path are Batch 4.

## Batch 4 notes

Two ways to scan a Docker image, both via Trivy:
- `POST /projects/{id}/scans` with `scan_type: "docker_image"` and `target: "<registry-ref>"`
  (e.g. `nginx:1.27`) — Trivy pulls and scans it directly, no upload needed.
- `POST /projects/{id}/scans/docker-image` (multipart) with a `.tar` from `docker save` — the file
  is written to `UPLOAD_DIR` (shared between `backend`/`worker` via the existing bind mount),
  scanned with `trivy image --input`, then deleted once the scan finishes.

`backend/app/scanner/image_scanner.py` parses Trivy's JSON `Results[].Vulnerabilities[]` into the
same `Finding` shape the repo scanner uses, so `Vulnerability` rows and the `security_score`
formula (`backend/app/scanner/scoring.py`, shared by both engines) are consistent across scan
types. Trivy is installed via its official install script in the backend Docker image.

## Batch 5 notes

`GET /dashboard/summary` returns one payload for the whole dashboard: average `security_score`
across completed scans, project/scan counts, a severity breakdown (count per severity across all
vulnerabilities), the 5 most recent scans, the 10 most recent critical/high findings, and a
14-day daily vulnerability count for the trend chart. All aggregation SQL lives in
`backend/app/repositories/dashboard_repository.py` (joins Vulnerability→Scan→Project, scoped to
`Project.owner_id` for regular users, unscoped for admins).

Frontend: `DashboardPage.tsx` wires this into stat cards plus two Recharts widgets (severity bar
chart, vulnerability trend line chart) via React Query.

## Batch 6 notes

`POST /scans/{id}/reports` with `{"format": "json"}` or `{"format": "pdf"}` generates a report
file from the scan's persisted vulnerabilities (only allowed once `Scan.status == completed`),
writes it under `REPORTS_DIR`, and records a `Report` row. `GET /scans/{id}/reports` lists past
reports; `GET /reports/{id}/download` streams the file back.

- JSON report (`app/reporting/json_report.py`): scan metadata + findings, each with a `cve_url`
  built from `CVE_LOOKUP_URL` (NVD) when a `cve_id` is present.
- PDF report (`app/reporting/pdf_report.py`, via `reportlab`): a findings table with the same
  CVE values rendered as clickable links, severity-colored.

## Batch 7 notes

New pages, all behind `ProtectedRoute` and sharing a `Layout`/`NavBar`:
- `/projects` — create + list projects.
- `/projects/:projectId` — create a repository scan (target URL) or upload a `docker save` `.tar`
  for image scanning; live-polls the scans list every 5s.
- `/scans/:scanId` — polls scan status until `completed`/`failed`, then shows the vulnerability
  table with client-side search (title/package/CVE), severity filter, date sort, clickable CVE
  links to NVD, and report generation/download (JSON/PDF) wired to Batch 6's endpoints.

Report downloads go through `apiClient` (blob + object URL), not a plain `<a href>`, because the
download endpoint requires the JWT bearer header — a direct browser navigation wouldn't carry it.

## Batch 8 notes

- **Tests**: `backend/tests/` uses an in-memory SQLite DB (via `get_db` dependency override) and
  monkeypatches both Celery tasks' `.delay` to no-ops, so the suite runs with no Postgres/Redis
  required: `cd backend && pytest -v`. Covers auth (register/login/me, duplicate email, bad
  password, missing token), project ownership isolation, and scan creation/ownership checks.
- **CI**: `.github/workflows/ci.yml` runs `pytest` on every push/PR and `npm run build`
  (`tsc -b && vite build`) for the frontend, as two parallel jobs.
- **Nginx / production deploy**: `docker/docker-compose.prod.yml` + `frontend/Dockerfile.prod`
  build the React app as static files served by Nginx (`frontend/nginx.conf`), which also
  reverse-proxies `/api/` to the backend. Backend/worker run without `--reload` and without the
  dev bind-mounts. Run with `docker compose -f docker/docker-compose.prod.yml up --build`.
- **Swagger**: `/docs` now has a real title, description, version, and per-tag descriptions
  (auth/projects/scans/reports/dashboard) instead of FastAPI's bare defaults.

## All 8 batches complete

The full vertical slice from design.md/tech_stack.md is implemented: JWT+RBAC auth, projects,
repository scanning (Gitleaks/Semgrep/pip-audit/Safety) and Docker image scanning (Trivy) via
Celery, a dashboard with aggregated metrics, PDF/JSON reports with CVE links, a complete React
frontend, and tests/CI/production deploy config. Stretch goals (GitHub OAuth, scheduled scans,
email alerts, GitHub Actions integration *into scans*, multi-project workspaces) are not started.

First migration (after containers are up):

```
docker compose -f docker/docker-compose.yml exec backend alembic revision --autogenerate -m "create users table"
docker compose -f docker/docker-compose.yml exec backend alembic upgrade head
```
