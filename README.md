# 🎲 D&D Character Manager

**A FastAPI + PostgreSQL backend for creating and managing D&D characters.**

D&D Character Manager is a portfolio project built around a simple idea: make character management easier by keeping characters, spells, and D&D reference data in one place.

The project currently focuses on the backend and REST API, with a frontend planned as the next major stage.

---

## ✨ Features

* 🔐 JWT authentication and authorization
* 👤 User accounts and profile management
* 🧙 Per-user character CRUD
* 🧝 D&D races
* ⚔️ D&D classes
* 📜 Character backgrounds
* ✨ Spells and character spell management
* 👑 Admin-only reference data and user management
* 🗃️ PostgreSQL database
* 🔄 Alembic database migrations
* 🧪 Automated API tests
* 📖 Interactive Swagger documentation
* ❤️ Health check endpoint

---

## 🛠️ Tech Stack

| Technology       | Purpose                     |
| ---------------- | --------------------------- |
| **Python 3.13**  | Core language               |
| **FastAPI**      | REST API framework          |
| **SQLAlchemy 2** | ORM and database access     |
| **PostgreSQL**   | Relational database         |
| **Alembic**      | Database migrations         |
| **Pydantic**     | Data validation and schemas |
| **JWT**          | Authentication              |
| **Pytest**       | Automated testing           |
| **Ruff**         | Linting and formatting      |
| **uv**           | Dependency management       |

---

## 🏗️ Architecture

The backend is organized by responsibility:

```text
dnd-character-manager/
│
├── alembic/
│   └── versions/
│
├── dependencies/
│   └── authentication & authorization dependencies
│
├── models/
│   └── SQLAlchemy ORM models
│
├── routers/
│   └── API endpoints
│
├── schemas/
│   └── Pydantic request/response schemas
│
├── seed/
│   └── D&D reference data
│
├── tests/
│   └── pytest test suite
│
├── config.py
├── database.py
├── security.py
├── main.py
├── alembic.ini
├── pyproject.toml
└── README.md
```

The project keeps API routes, database models, validation schemas, authentication, and configuration separated so the application can grow without turning into a single large module.

---

## 🔐 Authentication

The API uses JWT-based authentication.

```text
Registration
     ↓
Login
     ↓
JWT access token
     ↓
Authenticated requests
```

### Current authentication functionality

* User registration
* Login with OAuth2 password flow
* JWT access tokens
* Password hashing
* Current-user endpoint
* Password change
* Role-based authorization
* Admin password reset

Access tokens expire after **30 minutes by default**.

> Refresh tokens are not implemented yet. When an access token expires, the user must log in again.

---

## 🧙 Characters

Characters are the core entity of the application.

Each character can have:

* Name
* Level
* Race
* Class
* Background
* Ability scores
* Known spells

Characters belong to individual users, and ownership is enforced by the API.

Another user's character is intentionally returned as `404 Not Found` rather than `403 Forbidden`, preventing character existence from being exposed.

### Character reference data

Character responses include both reference IDs and expanded reference objects:

```json
{
  "id": 1,
  "name": "Arwen",
  "level": 5,
  "race_id": 2,
  "class_id": 1,
  "background_id": 3,
  "race": {
    "id": 2,
    "name": "Elf",
    "description": "...",
    "speed": 30
  },
  "character_class": {
    "id": 1,
    "name": "Wizard"
  },
  "background": {
    "id": 3,
    "name": "Sage"
  },
  "strength": 10,
  "dexterity": 14,
  "constitution": 12,
  "intelligence": 16,
  "wisdom": 13,
  "charisma": 15
}
```

The field is called `character_class` rather than `class` to avoid ambiguity with Python and framework conventions.

---

## ✨ Spells

Spells are available as shared reference data and can be assigned to individual characters.

The API supports:

* Spell CRUD
* Pagination
* Level filtering
* School filtering
* Name search
* Adding spells to characters
* Removing spells from characters
* Duplicate prevention

### Example

```text
GET /spells?level=3&school=evocation&search=fire&limit=50&offset=0
```

Response:

```json
{
  "items": [],
  "total": 319,
  "limit": 50,
  "offset": 0
}
```

The spell endpoint is paginated because the reference dataset can grow significantly larger than the other reference resources.

---

## 📖 API Documentation

Once the development server is running:

**Swagger UI**

```text
http://localhost:8000/docs
```

**ReDoc**

```text
http://localhost:8000/redoc
```

Swagger is the easiest way to explore and manually test the API.

---

## 🔌 API Endpoints

### Health

| Method | Endpoint  | Auth |
| ------ | --------- | ---- |
| GET    | `/health` | —    |

### Users

| Method | Endpoint              | Auth |
| ------ | --------------------- | ---- |
| POST   | `/users/registration` | —    |
| POST   | `/users/login`        | —    |
| GET    | `/users/me`           | User |
| PATCH  | `/users/me`           | User |

### Characters

| Method | Endpoint           | Auth |
| ------ | ------------------ | ---- |
| GET    | `/characters`      | User |
| POST   | `/characters`      | User |
| GET    | `/characters/{id}` | User |
| PATCH  | `/characters/{id}` | User |
| DELETE | `/characters/{id}` | User |

### Character spells

| Method | Endpoint                             | Auth |
| ------ | ------------------------------------ | ---- |
| GET    | `/characters/{id}/spells`            | User |
| POST   | `/characters/{id}/spells`            | User |
| DELETE | `/characters/{id}/spells/{spell_id}` | User |

### Reference data

| Resource    | Public | Admin                 |
| ----------- | ------ | --------------------- |
| Races       | GET    | POST / PATCH / DELETE |
| Classes     | GET    | POST / PATCH / DELETE |
| Backgrounds | GET    | POST / PATCH / DELETE |
| Spells      | GET    | POST / PATCH / DELETE |

### Administration

Admin users can manage users through the `/admin/users...` endpoints.

For the complete API reference, see Swagger.

---

## 🚀 Quick Start

### Requirements

* Python 3.13
* PostgreSQL
* `uv`

### 1. Clone the repository

```bash
git clone https://github.com/annastasiiah/dnd-character-manager.git
cd dnd-character-manager
```

### 2. Install dependencies

```bash
uv sync
```

`uv` uses `pyproject.toml` and `uv.lock` to install the project dependencies.

### 3. Configure environment variables

Copy the example configuration:

```bash
cp .env.example .env
```

At minimum, configure:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/dnd_manager
SECRET_KEY=your-secret-key
```

Generate a secure secret key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

`.env` is gitignored. Changes to environment configuration should be reflected in `.env.example`.

### 4. Create databases

```bash
createdb dnd_manager
createdb dnd_manager_test
```

### 5. Run migrations

```bash
uv run alembic upgrade head
```

### 6. Load reference data

```bash
uv run python -m seed
```

This loads the initial races, classes, backgrounds, and spells.

### 7. Start the server

```bash
uv run uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Health check:

```text
GET /health
```

---

## ⚙️ Environment Variables

| Variable                      | Required   | Default                 | Purpose                           |
| ----------------------------- | ---------- | ----------------------- | --------------------------------- |
| `DATABASE_URL`                | Yes        | —                       | PostgreSQL DSN                    |
| `SECRET_KEY`                  | Yes        | —                       | JWT signing key                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No         | `30`                    | Access-token lifetime             |
| `CORS_ORIGINS`                | No         | `http://localhost:5173` | Allowed browser origins           |
| `TEST_DATABASE_URL`           | Tests only | Local test DB           | PostgreSQL database used by tests |

Configuration is loaded and validated centrally in `config.py`.

Missing required configuration causes the application to fail at startup with a clear validation error.

---

## 🧪 Testing

The project uses **pytest** and runs the test suite against a real PostgreSQL database.

```bash
uv run pytest
```

The test database must be separate from the development database because test fixtures clean up database rows between tests.

The current test suite contains **160 tests** covering:

* Authentication
* User management
* Authorization
* Characters
* Races
* Classes
* Backgrounds
* Spells
* Character spells
* Validation
* Error handling
* Health checks

### Linting and formatting

```bash
uv run ruff check .
uv run ruff format .
```

---

## 🌐 Frontend Integration

The backend is designed to be consumed by a separate frontend application.

### Base URL

```text
http://localhost:8000
```

There is currently no `/api` prefix.

Collection routes do not use trailing slashes:

```text
GET /classes
```

rather than:

```text
GET /classes/
```

### Login

`POST /users/login` uses an OAuth2-compatible form body rather than JSON.

```typescript
const body = new URLSearchParams({
  username: email,
  password,
});

const response = await fetch(`${API}/users/login`, {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body,
});

const {
  access_token,
  token_type,
  expires_in,
} = await response.json();
```

Protected requests use:

```text
Authorization: Bearer <access_token>
```

`expires_in` is returned in seconds and is `1800` by default.

---

## 📡 API Error Handling

The API follows consistent HTTP status codes:

| Status | Meaning                            |
| ------ | ---------------------------------- |
| `201`  | Resource created                   |
| `204`  | Resource deleted                   |
| `400`  | Invalid request / empty PATCH      |
| `401`  | Authentication required or invalid |
| `403`  | Insufficient permissions           |
| `404`  | Resource not found                 |
| `409`  | Duplicate or conflicting resource  |
| `422`  | Request validation error           |

Most errors use:

```json
{
  "detail": "Error message"
}
```

FastAPI validation errors (`422`) use the standard array of field-level errors.

---

## 🗄️ Database Migrations

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Always review autogenerated migrations before committing them.

When the schema changes, the test database must also be migrated.

---

## 🌱 Project Status

**🚧 In active development**

The backend API is currently the main focus. The next major stage is building the frontend and connecting it to the existing REST API.

The long-term goal is to turn D&D Character Manager into a complete full-stack application for managing D&D characters and their adventures.

---

## 👩‍💻 About the Project

This project is part of my transition from mathematics and teaching into software development.

I am using it to explore how a real application evolves from database models and REST endpoints into a complete full-stack product.

The project combines things I genuinely enjoy — **Python, software development, games, fantasy worlds, and problem solving.**

---

<p align="center">
  🎲 Built with Python, FastAPI & a little bit of magic ✨
</p>
