from tests.conftest import auth_headers, register_and_login


def _create_project(client, token, name="demo"):
    return client.post("/api/v1/projects", json={"name": name}, headers=auth_headers(token)).json()


def test_create_repository_scan_starts_pending(client):
    token = register_and_login(client)
    project = _create_project(client, token)

    response = client.post(
        f"/api/v1/projects/{project['id']}/scans",
        json={"scan_type": "repository", "target": "https://github.com/org/repo.git"},
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    scan = response.json()
    assert scan["status"] == "pending"
    assert scan["scan_type"] == "repository"


def test_scan_requires_project_ownership(client):
    owner_token = register_and_login(client, "owner2@example.com")
    project = _create_project(client, owner_token)

    other_token = register_and_login(client, "other2@example.com")
    response = client.post(
        f"/api/v1/projects/{project['id']}/scans",
        json={"scan_type": "repository", "target": "https://github.com/org/repo.git"},
        headers=auth_headers(other_token),
    )
    assert response.status_code == 403


def test_list_scans_for_project(client):
    token = register_and_login(client)
    project = _create_project(client, token)
    client.post(
        f"/api/v1/projects/{project['id']}/scans",
        json={"scan_type": "repository", "target": "https://github.com/org/repo.git"},
        headers=auth_headers(token),
    )

    response = client.get(f"/api/v1/projects/{project['id']}/scans", headers=auth_headers(token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_unknown_scan_returns_404(client):
    token = register_and_login(client)
    response = client.get(
        "/api/v1/scans/00000000-0000-0000-0000-000000000000", headers=auth_headers(token)
    )
    assert response.status_code == 404
