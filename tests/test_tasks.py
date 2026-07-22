def test_tasks_require_auth(client):
    resp = client.get("/api/tasks")
    assert resp.status_code == 401


def test_create_task(client, auth_headers):
    resp = client.post(
        "/api/tasks",
        json={"title": "Write tests", "description": "cover the API"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Write tests"
    assert body["completed"] is False
    assert "id" in body


def test_create_task_missing_title(client, auth_headers):
    resp = client.post("/api/tasks", json={"description": "no title"}, headers=auth_headers)
    assert resp.status_code == 400


def test_list_tasks(client, auth_headers):
    client.post("/api/tasks", json={"title": "T1"}, headers=auth_headers)
    client.post("/api/tasks", json={"title": "T2"}, headers=auth_headers)
    resp = client.get("/api/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()["tasks"]) == 2


def test_get_single_task(client, auth_headers):
    created = client.post("/api/tasks", json={"title": "T1"}, headers=auth_headers).get_json()
    resp = client.get(f"/api/tasks/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "T1"


def test_get_missing_task(client, auth_headers):
    resp = client.get("/api/tasks/999", headers=auth_headers)
    assert resp.status_code == 404


def test_update_task(client, auth_headers):
    created = client.post("/api/tasks", json={"title": "T1"}, headers=auth_headers).get_json()
    resp = client.put(
        f"/api/tasks/{created['id']}",
        json={"title": "Updated", "completed": True},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["title"] == "Updated"
    assert body["completed"] is True


def test_delete_task(client, auth_headers):
    created = client.post("/api/tasks", json={"title": "T1"}, headers=auth_headers).get_json()
    resp = client.delete(f"/api/tasks/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200

    # It should be gone now.
    resp = client.get(f"/api/tasks/{created['id']}", headers=auth_headers)
    assert resp.status_code == 404


def test_users_cannot_see_others_tasks(client, auth_headers):
    # alice (from fixture) creates a task
    client.post("/api/tasks", json={"title": "alice task"}, headers=auth_headers)

    # bob registers, logs in, and lists tasks
    client.post("/api/register", json={"username": "bob", "password": "pw12345"})
    token = client.post(
        "/api/login", json={"username": "bob", "password": "pw12345"}
    ).get_json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/tasks", headers=bob_headers)
    assert resp.status_code == 200
    assert resp.get_json()["tasks"] == []
