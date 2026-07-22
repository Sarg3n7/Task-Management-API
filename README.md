# Task Management API

A small REST API built with **Flask-RESTful**, **SQLite** (via SQLAlchemy), and
**JWT authentication**. Supports user registration, login, and full CRUD on tasks.
Each user only sees their own tasks.

## Tech stack
- Flask + Flask-RESTful — routing / resources
- Flask-SQLAlchemy — ORM over SQLite
- Flask-JWT-Extended — JWT auth
- pytest — tests

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                 # serves at http://localhost:5000
```

## Endpoints

| Method | Path                  | Auth | Description        |
|--------|-----------------------|------|--------------------|
| POST   | /api/register         | No   | Create an account  |
| POST   | /api/login            | No   | Get a JWT token    |
| GET    | /api/tasks            | Yes  | List your tasks    |
| POST   | /api/tasks            | Yes  | Create a task      |
| GET    | /api/tasks/<id>       | Yes  | Get one task       |
| PUT    | /api/tasks/<id>       | Yes  | Update a task      |
| DELETE | /api/tasks/<id>       | Yes  | Delete a task      |

Send the token as a header on protected routes:
`Authorization: Bearer <access_token>`

## Running tests

```bash
pytest -q
```
