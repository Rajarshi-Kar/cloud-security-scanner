from tests.conftest import auth_headers, register_and_login


def test_register_and_login_flow(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "password": "Sup3rSecret!", "full_name": "Alice"},
    )
    assert register_response.status_code == 201
    body = register_response.json()
    assert body["email"] == "alice@example.com"
    assert body["role"] == "user"

    login_response = client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "Sup3rSecret!"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "alice@example.com"


def test_register_duplicate_email_fails(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "bob@example.com", "password": "Sup3rSecret!", "full_name": "Bob"},
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "bob@example.com", "password": "Sup3rSecret!", "full_name": "Bob"},
    )
    assert response.status_code == 409


def test_login_with_wrong_password_fails(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "carol@example.com", "password": "Sup3rSecret!", "full_name": "Carol"},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "carol@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_me_without_token_is_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_register_and_login_helper(client):
    token = register_and_login(client)
    response = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert response.status_code == 200
