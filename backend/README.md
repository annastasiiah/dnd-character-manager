## D&D Character Manager — Backend

A REST API for creating and managing Dungeons & Dragons characters, built with FastAPI, PostgreSQL, and SQLAlchemy. The project includes JWT authentication, database migrations, and asynchronous PDF character sheet exports.

## Features

- **Authentication** — user registration and login with JWT access tokens.
- **Character management** — create, retrieve, update, and delete characters.
- **Character details** — races, classes, backgrounds, ability scores, and spells.
- **Spell API** — retrieve spells and explore available spell schools.
- **Authorization** — protected endpoints and user-specific character access.
- **PDF exports** — generate character sheets asynchronously with Celery and download completed PDFs.
- **Database migrations** — manage schema changes with Alembic.
- **Containerized environment** — run the API and supporting services with Docker Compose.
- **Interactive API documentation** — explore and test endpoints through Swagger UI.

## Tech Stack

| Category | Technologies |
|---|---|
| Language | Python 3.13 |
| API | FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy 2.0 |
| Validation | Pydantic |
| Migrations | Alembic |
| Authentication | JWT, password hashing |
| Background tasks | Celery, Redis |
| PDF generation | ReportLab |
| Dependency management | uv |
| Infrastructure | Docker, Docker Compose |

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine with the Compose plugin
- Git

Docker Compose is the recommended way to run the backend because it starts the API and its supporting services together.

### 1. Clone the repository

```bash
git clone https://github.com/annastasiiah/dnd-character-manager.git
cd dnd-character-manager/backend
```

### 2. Configure environment variables

Review `docker-compose.yml` and the application's settings before starting the services.

The local Docker configuration uses a PostgreSQL database, a development secret key, and a frontend origin of `http://localhost:5173`.

If you use a `.env` file, configure the required database connection, JWT secret, token expiration, CORS origins, and any Redis or export settings required by your configuration.

**Important:** The default credentials and secrets used for local development are not suitable for production. Never commit real secrets or your `.env` file.

### 3. Start the services

```bash
docker compose up -d --build
```

Check that the containers are running:

```bash
docker compose ps
```

View logs when troubleshooting:

```bash
docker compose logs --tail=100 api
docker compose logs --tail=100 worker
```

### 4. Apply database migrations

```bash
docker compose exec api uv run alembic upgrade head
```

### 5. Open the API documentation

Once the API is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Use Swagger UI to inspect endpoints, authorize requests, and try the API interactively.

## API Overview

The API is organized into resource-based endpoints. The following are the main entry points; consult `/docs` for the current request schemas, response formats, and available operations.

| Resource | Endpoint | Purpose |
|---|---|---|
| Authentication | `POST /users/registration` | Register a user |
| Authentication | `POST /users/login` | Log in and obtain an access token |
| Characters | `/characters` | Manage characters belonging to the authenticated user |
| Character exports | `POST /characters/{character_id}/export` | Start an asynchronous PDF export |
| Export status | `GET /characters/exports/{task_id}` | Check export progress |
| PDF download | `GET /characters/exports/{task_id}/download` | Download a completed PDF |
| Spells | `/spells` | Browse and search spells |
| Spell schools | `GET /spells/schools` | Retrieve available spell schools |
| Races | `/races` | Retrieve available character races |

Protected endpoints require a valid access token. Register or log in, then use the **Authorize** control in Swagger UI to authenticate requests.

## Asynchronous PDF Export

PDF generation runs in a background Celery worker, so the initial request does not need to wait for the file to be generated.

1. Send `POST /characters/{character_id}/export`.
2. Save the returned `task_id`.
3. Poll `GET /characters/exports/{task_id}` until the status becomes `SUCCESS` or `FAILURE`.
4. When the export succeeds, download the file through `GET /characters/exports/{task_id}/download`.

The API checks export ownership before returning status information or a PDF file.

## Database Migrations

Create a new migration after changing SQLAlchemy models:

```bash
docker compose exec api uv run alembic revision --autogenerate -m "describe your change"
```

Review the generated migration before applying it:

```bash
docker compose exec api uv run alembic upgrade head
```

Check the current migration revision:

```bash
docker compose exec api uv run alembic current
```

Do not apply autogenerated migrations without reviewing them first.

## Project Structure

```text
backend/
├── alembic/              # Database migrations
├── dependencies/         # Shared dependencies, including authentication
├── exporting/            # PDF generation
├── models/               # SQLAlchemy models
├── routers/              # FastAPI route handlers
├── schemas/              # Pydantic request and response schemas
├── tasks/                # Celery background tasks
├── tests/                # Automated tests
├── main.py               # FastAPI application entry point
├── database.py           # Database configuration
├── celery_app.py         # Celery application configuration
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── alembic.ini
```

## Development

For local development outside Docker, install Python 3.13 and [uv](https://docs.astral.sh/uv/), then install the project dependencies:

```bash
uv sync
```

The database and other required services must be available, and the environment variables must point to the correct services.

Run the API locally:

```bash
uv run uvicorn main:app --reload
```

Run the test suite:

```bash
uv run pytest
```

## Current Status

The backend supports authentication, character management, spell-related endpoints, database migrations, and asynchronous PDF exports. The frontend is planned as a separate part of the project.

## Roadmap

- [x] REST API and database models
- [x] User authentication and protected resources
- [x] Database migrations
- [x] Docker-based development environment
- [x] Asynchronous PDF character sheet export
- [ ] React and TypeScript frontend
- [ ] End-to-end testing of the complete application

## License

Add a `LICENSE` file to the repository if you intend to distribute the project under an open-source license.
