def test_register_success(client):
    resp = client.post(
        "/api/register",
        json={"username": "bob", "password": "pw12345"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["message"] == "user registered successfully"


def test_register_missing_fields(client):
    resp = client.post("/api/register", json={"username": "bob"})
    assert resp.status_code == 400


def test_register_duplicate_username(client):
    client.post("/api/register", json={"username": "bob", "password": "pw12345"})
    resp = client.post("/api/register", json={"username": "bob", "password": "other"})
    assert resp.status_code == 409


def test_login_success_returns_token(client):
    client.post("/api/register", json={"username": "bob", "password": "pw12345"})
    resp = client.post("/api/login", json={"username": "bob", "password": "pw12345"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/api/register", json={"username": "bob", "password": "pw12345"})
    resp = client.post("/api/login", json={"username": "bob", "password": "nope"})
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post("/api/login", json={"username": "ghost", "password": "x"})
    assert resp.status_code == 401
