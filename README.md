# Task Management API

A REST API for managing personal to-do tasks, built with **Flask-RESTful**, **SQLite**
(via SQLAlchemy), and **JWT authentication**. Users register, log in to receive a token,
and then create, read, update, and delete their own tasks. Every task belongs to one user,
and the API guarantees a user can only ever see or modify their own tasks.

---

## Tech stack

| Layer          | Tool               | Role                                              |
|----------------|--------------------|---------------------------------------------------|
| Web framework  | Flask              | Routing and HTTP handling                         |
| API layer      | Flask-RESTful      | Class-based `Resource` endpoints, JSON responses  |
| ORM            | Flask-SQLAlchemy   | Maps Python classes to tables; no raw SQL         |
| Database       | SQLite             | Zero-config, file-based (`tasks.db`)              |
| Auth           | Flask-JWT-Extended | Signed JWT access tokens (stateless auth)         |
| Passwords      | Werkzeug security  | Salted PBKDF2 hashing                             |
| Testing        | pytest             | Unit/integration test suite                       |

---

## Directory structure

```
task-manager-api/
├── app/
│   ├── __init__.py        # app factory: create_app()  (only init with code)
│   ├── config.py          # config + test config (in-memory DB)
│   ├── extensions.py      # db + jwt instances
│   ├── models.py          # User and Task models
│   └── resources/
│       ├── __init__.py    # EMPTY (package marker)
│       ├── auth.py        # /api/register, /api/login
│       └── tasks.py       # /api/tasks CRUD
├── tests/
│   ├── __init__.py        # EMPTY (package marker)
│   ├── conftest.py        # pytest fixtures
│   ├── test_auth.py
│   └── test_tasks.py
├── requirements.txt
├── run.py                 # entry point
└── README.md
```

> **Note:** Only `app/__init__.py` contains code (the `create_app` factory). The
> `resources/__init__.py` and `tests/__init__.py` files must be **empty** — they only
> mark those folders as Python packages.

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS / Linux / Git Bash
venv\Scripts\activate             # Windows PowerShell / CMD

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python run.py
```

The API serves at **http://localhost:5000**. On first run it auto-creates `tasks.db`.

---

## A note on curl and your shell

The examples below use standard `curl` syntax, which works as-is in **macOS/Linux
terminals** and **Git Bash** on Windows.

In **Windows PowerShell**, `curl` is an alias for `Invoke-WebRequest` and will reject the
`-H`/`-d` flags. On PowerShell, either:

- call real curl explicitly with `curl.exe` and put the command on one line, escaping the
  inner quotes: `-d "{\"username\":\"demo\",\"password\":\"pw123\"}"`, **or**
- use the native `Invoke-RestMethod` (headers are a hashtable: `-Headers @{ Authorization = "Bearer $token" }`), **or**
- just run the commands in **Git Bash**, where they work unchanged.

---

## Authentication flow

1. **Register** a user (`POST /api/register`).
2. **Log in** (`POST /api/login`) to receive a JWT `access_token`.
3. Send that token on every task request as a header:
   `Authorization: Bearer <access_token>`.

The token is signed (not encrypted) and its identity is the user's id. Protected routes
verify the signature and scope all data to the calling user.

### Grab a token into a variable (Git Bash / Linux / macOS)

```bash
TOKEN=$(curl -s -X POST localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"pw123"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
```

Then reuse `$TOKEN` in the task commands below. (If `python` isn't on your PATH in Git
Bash, log in manually and copy the `access_token`, then `TOKEN='paste_here'`.)

---

## Endpoint reference

Base URL: `http://localhost:5000`

| Method | Path                | Auth | Purpose               |
|--------|---------------------|------|-----------------------|
| POST   | `/api/register`     | No   | Create an account     |
| POST   | `/api/login`        | No   | Get a JWT token       |
| GET    | `/api/tasks`        | Yes  | List your tasks       |
| POST   | `/api/tasks`        | Yes  | Create a task         |
| GET    | `/api/tasks/<id>`   | Yes  | Get one task          |
| PUT    | `/api/tasks/<id>`   | Yes  | Update a task         |
| DELETE | `/api/tasks/<id>`   | Yes  | Delete a task         |

---

### 1. Register — `POST /api/register`

Creates a new user. No auth required.

**Request body**

| Field    | Type   | Required | Notes             |
|----------|--------|----------|-------------------|
| username | string | yes      | Must be unique    |
| password | string | yes      | Stored hashed     |

**Responses**

- `201 Created` — `{"message": "user registered successfully", "id": 1}`
- `400 Bad Request` — a field is missing
- `409 Conflict` — username already exists

```bash
curl -X POST localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"pw123"}'
```

---

### 2. Login — `POST /api/login`

Verifies credentials and returns a JWT. No auth required.

**Request body:** same `username` / `password` fields as register.

**Responses**

- `200 OK` — `{"access_token": "<jwt>"}`
- `400 Bad Request` — a field is missing
- `401 Unauthorized` — wrong username or password

```bash
curl -X POST localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"pw123"}'
```

---

### 3. List tasks — `GET /api/tasks`

Returns all tasks belonging to the authenticated user. Requires auth.

**Response**

- `200 OK`

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy milk",
      "description": "2%",
      "completed": false,
      "created_at": "2026-07-22T04:26:44.280067",
      "user_id": 1
    }
  ]
}
```

- `401 Unauthorized` — missing or invalid token

```bash
curl -X GET localhost:5000/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```

---

### 4. Create task — `POST /api/tasks`

Creates a task owned by the authenticated user. Requires auth.

**Request body**

| Field       | Type    | Required | Default | Notes           |
|-------------|---------|----------|---------|-----------------|
| title       | string  | yes      | —       | Task title      |
| description | string  | no       | `""`    | Free text       |
| completed   | boolean | no       | `false` | Done or not     |

**Responses**

- `201 Created` — returns the created task object
- `400 Bad Request` — `title` is missing
- `401 Unauthorized` — missing or invalid token

```bash
curl -X POST localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Buy milk","description":"2%"}'
```

---

### 5. Get one task — `GET /api/tasks/<id>`

Returns a single task by id, only if it belongs to the caller. Requires auth.

**Responses**

- `200 OK` — the task object
- `404 Not Found` — no such task, or it isn't yours
- `401 Unauthorized` — missing or invalid token

```bash
curl -X GET localhost:5000/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

### 6. Update task — `PUT /api/tasks/<id>`

Updates a task you own. Any of `title`, `description`, `completed` may be sent; **omitted
fields keep their current value**. Requires auth.

**Responses**

- `200 OK` — the updated task object
- `404 Not Found` — no such task, or it isn't yours
- `401 Unauthorized` — missing or invalid token

```bash
curl -X PUT localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Buy oat milk","completed":true}'
```

---

### 7. Delete task — `DELETE /api/tasks/<id>`

Deletes a task you own. Requires auth.

**Responses**

- `200 OK` — `{"message": "task deleted"}`
- `404 Not Found` — no such task, or it isn't yours
- `401 Unauthorized` — missing or invalid token

```bash
curl -X DELETE localhost:5000/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## Status codes summary

| Code | Meaning       | When                                              |
|------|---------------|---------------------------------------------------|
| 200  | OK            | Successful read, update, or delete                |
| 201  | Created       | New user or task created                          |
| 400  | Bad Request   | Missing required field                            |
| 401  | Unauthorized  | Missing/invalid token, or wrong login credentials |
| 404  | Not Found     | Task doesn't exist or isn't yours                 |
| 409  | Conflict      | Username already taken                            |

---

## Running tests

```bash
pytest -q
```

Tests run against a fresh **in-memory** SQLite database, so they are isolated and never
touch your real `tasks.db`.