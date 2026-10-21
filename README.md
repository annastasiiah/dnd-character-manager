# 🎲 D&D Character Manager

**A full-stack Dungeons & Dragons character management application.**

[![Backend CI](https://github.com/annastasiiah/dnd-character-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/annastasiiah/dnd-character-manager/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-TypeScript-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

D&D Character Manager is a full-stack application for creating, organizing, and managing D&D characters. It combines a React frontend with a FastAPI REST API and PostgreSQL database, with authentication, spell management, and background PDF exports.

The project demonstrates backend development, database design, API security, asynchronous task processing, automated testing, and Docker-based deployment.

## ✨ Features

- 🔐 **Authentication and authorization** — user registration, login, JWT access tokens, password hashing, and role-based access control.
- 🧙 **Character management** — create, view, update, and delete characters with ability scores and character details.
- 🧝 **D&D reference data** — races, classes, and backgrounds.
- ✨ **Spell management** — browse and filter spells, search by name, and manage spells assigned to characters.
- 👤 **User profiles** — view and update account information.
- 👑 **Administration** — administrative user management and protected reference-data operations.
- 📄 **PDF export** — generate character sheets through background tasks.
- 🗃️ **Relational database** — PostgreSQL with SQLAlchemy ORM and Alembic migrations.
- 🧪 **Automated tests** — API tests with pytest.
- 🔍 **Code quality checks** — Ruff linting and GitHub Actions CI.
- 📖 **Interactive API documentation** — Swagger UI and ReDoc.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.13 | Backend language |
| FastAPI | REST API |
| React + TypeScript | Frontend |
| Vite | Frontend development and build tooling |
| PostgreSQL | Relational database |
| SQLAlchemy 2 | ORM and database access |
| Alembic | Database schema migrations |
| Pydantic | Data validation |
| JWT | Authentication |
| Celery | Background task processing |
| Redis | Celery message broker and result backend |
| ReportLab | PDF generation |
| Pytest | Automated testing |
| Ruff | Python linting |
| uv | Python dependency management |
| Docker Compose | Local multi-service environment |
| GitHub Actions | Continuous integration |

## 🏗️ Architecture

The application is organized into separate frontend and backend components.

```text
dnd-character-manager/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── alembic/
│   ├── dependencies/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── seed/
│   ├── tasks/
│   ├── tests/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── celery_app.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── pyproject.toml
└── frontend/
    ├── src/
    ├── Dockerfile
    └── package.json
```

### How it works

1. The React frontend sends HTTP requests to the FastAPI backend.
2. FastAPI validates requests and applies authentication and authorization rules.
3. SQLAlchemy communicates with PostgreSQL.
4. Alembic manages database schema changes.
5. Celery processes PDF export tasks using Redis as its broker.
6. Docker Compose runs the frontend, API, database, Redis, and background worker as separate services.

## 🚀 Getting Started

The easiest way to run the complete application locally is with Docker Compose.

### Prerequisites

Install:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine with the Compose plugin

### 1. Clone the repository

```bash
git clone https://github.com/annastasiiah/dnd-character-manager.git
cd dnd-character-manager
```

### 2. Configure environment variables

Create your local environment file from the example:

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and set the following values:

```env
DATABASE_URL=postgresql+psycopg://dnd_user:changeme@localhost:5433/dnd_manager
SECRET_KEY=replace-me-with-a-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173
TEST_DATABASE_URL=postgresql+psycopg://dnd_user:changeme@localhost:5433/dnd_manager_test

POSTGRES_PASSWORD=change_me_to_a_long_random_password
```

Use your own strong values for `SECRET_KEY` and `POSTGRES_PASSWORD`. Keep the `.env` file private and never commit it to Git.

You can generate a JWT signing key with Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

The Docker Compose configuration supplies the correct internal PostgreSQL connection URL to the API and worker containers. The database is exposed on port `5433` on your host machine.

### 3. Build and start the services

From the repository root, run:

```bash
docker compose -f backend/docker-compose.yml up --build -d
```

Docker will build the frontend and backend images and start the following services:

| Service | Purpose | Local address |
|---|---|---|
| Frontend | React application | http://localhost:8080 |
| API | FastAPI backend | http://localhost:8000 |
| PostgreSQL | Database | `localhost:5433` |
| Redis | Background task broker | Internal Docker network |
| Worker | Asynchronous PDF exports | Internal Docker network |

### 4. Apply database migrations

On the first run, create the database schema by applying the migrations:

```bash
docker compose -f backend/docker-compose.yml exec api uv run alembic upgrade head
```

Alembic applies migrations to the application database configured by `DATABASE_URL`. `TEST_DATABASE_URL` is reserved for automated tests.

### 5. Load the reference data

Populate the database with the initial D&D races, classes, backgrounds, and spells:

```bash
docker compose -f backend/docker-compose.yml exec api uv run python -m seed
```

Run this initialization step when setting up a fresh database. If you restart the application later, you normally do not need to seed it again.

### 6. Open the application

Once the services are running, open:

- **Frontend:** http://localhost:8080
- **Swagger API documentation:** http://localhost:8000/docs
- **ReDoc API documentation:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

The health endpoint should return a JSON response indicating that the API is running.

### Useful Docker commands

Check service status:

```bash
docker compose -f backend/docker-compose.yml ps
```

View application logs:

```bash
docker compose -f backend/docker-compose.yml logs -f
```

View logs for a specific service:

```bash
docker compose -f backend/docker-compose.yml logs -f api
```

Stop the application:

```bash
docker compose -f backend/docker-compose.yml down
```

This stops and removes the containers while preserving named database and export volumes. **Do not add `-v`** unless you intentionally want to delete the persisted data.

## 🔌 API Overview

The REST API exposes endpoints for authentication, users, characters, spells, and reference data.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check API status |
| `POST` | `/users/registration` | Register an account |
| `POST` | `/users/login` | Authenticate and obtain a token |
| `GET` | `/users/me` | Retrieve the current user's profile |
| `PATCH` | `/users/me` | Update the current user's profile |
| `GET` | `/characters` | List the current user's characters |
| `POST` | `/characters` | Create a character |
| `GET` | `/characters/{id}` | Retrieve a character |
| `PATCH` | `/characters/{id}` | Update a character |
| `DELETE` | `/characters/{id}` | Delete a character |
| `GET` | `/spells` | Browse and filter spells |
| `GET` | `/races` | Browse races |
| `GET` | `/classes` | Browse classes |
| `GET` | `/backgrounds` | Browse backgrounds |

Additional endpoints support character spell management, reference-data administration, user administration, and PDF exports.

For request schemas, response examples, and the complete endpoint list, see the interactive documentation at `/docs`.

## 🔐 Authentication and Security

The API uses JWT bearer authentication to protect user-specific operations.

- Passwords are hashed before storage.
- Protected endpoints require a valid access token.
- Authorization rules restrict administrative operations.
- Character ownership is enforced by the backend.
- Access tokens expire after 30 minutes by default.
- Requests and responses are validated using FastAPI and Pydantic.

For protected endpoints, include the token in the request header:

```http
Authorization: Bearer <access_token>
```

## 🧪 Testing and Code Quality

The backend test suite uses pytest and PostgreSQL. Tests require a separate test database because fixtures modify database records.

To run the backend checks locally, first configure the test database using the instructions in `backend/.env.example`, then run:

```bash
cd backend

uv sync --frozen --all-groups

uv run ruff check .
DATABASE_URL="$TEST_DATABASE_URL" uv run alembic upgrade head
uv run pytest -q
```

Ensure that the database configuration points to the intended database before running tests. Do not use a database containing data you need to preserve.

GitHub Actions runs backend linting, database migrations, automated tests, and a PDF-generation check on pushes and pull requests targeting `main`.

[View CI workflow](https://github.com/annastasiiah/dnd-character-manager/actions/workflows/ci.yml)

## 🗄️ Database Migrations

Database schema changes are managed with Alembic.

Apply existing migrations:

```bash
cd backend
uv run alembic upgrade head
```

Generate a migration after changing SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

Review autogenerated migrations before committing them.

## 📌 Project Goals

This project is part of my journey from mathematics and teaching into software development.

I wanted to build something practical that combines problem-solving, backend engineering, databases, and my interest in tabletop role-playing games. The project is an opportunity to apply software development concepts in a growing application rather than isolated exercises.

The long-term goal is to continue improving the application and expand its functionality.

## 👩‍💻 Author

**Anastasiia Horpynyuk**

- GitHub: [@annastasiiah](https://github.com/annastasiiah)
- LinkedIn: [Connect with me](https://www.linkedin.com/in/anastasia-horpynyuk-0397a8420/)

---

<p align="center">
  Built with Python, React, and a little bit of fantasy magic 🎲✨
</p>
