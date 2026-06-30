from tests.conftest import auth_headers, register_and_login


def test_create_and_list_project(client):
    token = register_and_login(client)
    create_response = client.post(
        "/api/v1/projects", json={"name": "demo", "repo_url": "https://github.com/org/demo.git"},
        headers=auth_headers(token),
    )
    assert create_response.status_code == 201
    project = create_response.json()
    assert project["name"] == "demo"

    list_response = client.get("/api/v1/projects", headers=auth_headers(token))
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_project_isolated_between_users(client):
    owner_token = register_and_login(client, "owner@example.com")
    create_response = client.post(
        "/api/v1/projects", json={"name": "owner-project"}, headers=auth_headers(owner_token)
    )
    project_id = create_response.json()["id"]

    other_token = register_and_login(client, "other@example.com")
    get_response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers(other_token))
    assert get_response.status_code == 403

    list_response = client.get("/api/v1/projects", headers=auth_headers(other_token))
    assert list_response.json() == []


def test_delete_project(client):
    token = register_and_login(client)
    project_id = client.post(
        "/api/v1/projects", json={"name": "to-delete"}, headers=auth_headers(token)
    ).json()["id"]

    delete_response = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers(token))
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers(token))
    assert get_response.status_code == 404
