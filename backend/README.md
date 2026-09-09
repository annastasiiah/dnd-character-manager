# D&D Character Manager — Backend

FastAPI + PostgreSQL API for creating D&D characters: accounts and JWT auth,
per-user character CRUD, a character's known spells, and the shared reference
data (races, classes, backgrounds, spells) that the character form is built on.

- **Stack:** Python 3.13, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, `uv`
- **Interactive docs:** <http://localhost:8000/docs> once the server is running

---

## Quick start

```bash
# 1. Dependencies (uv reads pyproject.toml + uv.lock)
uv sync

# 2. Configuration
cp .env.example .env
# then edit .env — at minimum DATABASE_URL and SECRET_KEY.
# Generate a key with:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 3. Databases (once)
createdb dnd_manager
createdb dnd_manager_test

# 4. Schema
uv run alembic upgrade head

# 5. Reference data (races, classes, backgrounds, spells)
uv run python -m seed

# 6. Run
uv run uvicorn main:app --reload
```

The API is then on <http://localhost:8000> and `GET /health` should return
`{"status": "ok", ...}`.

### Environment variables

All configuration lives in `.env` and is read and validated once in
`config.py`, so a missing variable fails at startup with a clear message.

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | yes | — | PostgreSQL DSN, psycopg 3 driver |
| `SECRET_KEY` | yes | — | Signs the JWTs |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | no | `30` | Access-token lifetime |
| `CORS_ORIGINS` | no | `http://localhost:5173` | Comma-separated allowed browser origins |
| `TEST_DATABASE_URL` | tests only | local `dnd_manager_test` | Database the test suite truncates |

`.env` is gitignored. Commit changes to `.env.example` instead.

---

## Tests

```bash
uv run pytest
```

The suite runs against a **real PostgreSQL database** — `TEST_DATABASE_URL`,
or `dnd_manager_test` on localhost by default. It must be a separate database:
the fixtures delete every row between tests. Create it and migrate it once:

```bash
createdb dnd_manager_test
TEST_DATABASE_URL=... DATABASE_URL=<test db url> uv run alembic upgrade head
```

Lint and format:

```bash
uv run ruff check .
uv run ruff format .
```

---

## Frontend integration

**Base URL:** `http://localhost:8000` — no `/api` prefix, and no trailing
slashes on collection routes (`GET /classes`, not `GET /classes/`).

### Auth

`POST /users/login` takes a **form body**, not JSON — it is an OAuth2 password
flow, and the email goes in the field named `username`:

```ts
const body = new URLSearchParams({ username: email, password });

const res = await fetch(`${API}/users/login`, {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body,
});

const { access_token, token_type, expires_in } = await res.json();
```

Send it on every protected request as `Authorization: Bearer <access_token>`.
`expires_in` is seconds (1800 by default), so the client can schedule a
re-login without decoding the JWT. **There is no refresh endpoint yet** — when
a token expires the user logs in again. A 401 on any protected route means the
token is missing, malformed, or expired.

`GET /users/me` returns the current user including `role` (`"user"` or
`"admin"`), which is what an admin-only UI should gate on.

### Endpoints

Everything is under `/docs`, but in summary:

| Method | Path | Auth | Notes |
|---|---|---|---|
| `GET` | `/health` | — | Liveness + version |
| `POST` | `/users/registration` | — | `201`, returns the user (no token) |
| `POST` | `/users/login` | — | Form-encoded; returns the token |
| `GET` | `/users/me` | user | |
| `PATCH` | `/users/me` | user | `email`, `nickname`, `password` |
| `GET` | `/characters` | user | Own characters only |
| `POST` | `/characters` | user | `201` |
| `GET` | `/characters/{id}` | user | `404` if not yours |
| `PATCH` | `/characters/{id}` | user | Partial |
| `DELETE` | `/characters/{id}` | user | `204` |
| `GET` | `/characters/{id}/spells` | user | The character's known spells |
| `POST` | `/characters/{id}/spells` | user | `201`, body `{ "spell_id": n }` |
| `DELETE` | `/characters/{id}/spells/{spell_id}` | user | `204` |
| `GET` | `/races` `/classes` `/backgrounds` | — | Full list, public |
| `GET` | `/races/{id}` `/classes/{id}` `/backgrounds/{id}` | — | Public |
| `GET` | `/spells` | — | **Paginated** — see below |
| `GET` | `/spells/{id}` | — | Public |
| `POST` `PATCH` `DELETE` | `/races` `/classes` `/backgrounds` `/spells` | **admin** | Manage reference data |
| `GET` `PATCH` `DELETE` | `/admin/users…` | **admin** | User administration |

### Characters come with their reference data expanded

`CharacterResponse` carries both the raw ids (for edit forms) and the resolved
objects, so a character list renders without extra lookups:

```jsonc
{
  "id": 1,
  "name": "Arwen",
  "level": 5,
  "race_id": 2, "class_id": 1, "background_id": 3,
  "race": { "id": 2, "name": "Elf", "description": "…", "speed": 30 },
  "character_class": { "id": 1, "name": "Wizard" },
  "background": { "id": 3, "name": "Sage" },
  "strength": 10, "dexterity": 14, "constitution": 12,
  "intelligence": 16, "wisdom": 13, "charisma": 15,
  "created_at": "…", "updated_at": "…"
}
```

Note the field is `character_class`, not `class` — `class` is a reserved word
in too many places to be worth it.

### `GET /spells` is paginated

It is the one list that can grow large, so it returns an envelope and accepts
filters:

```
GET /spells?level=3&school=evocation&search=fire&limit=50&offset=0
```

```json
{ "items": [ … ], "total": 319, "limit": 50, "offset": 0 }
```

`limit` is 1–200 (default 50), `offset` ≥ 0, `school` is case-insensitive and
`search` matches anywhere in the name. Every other list route returns a plain
array.

### Status codes and errors

Consistent across the API:

- `201` for every create, `204` (empty body) for every delete
- `400` — a `PATCH` with no updatable fields
- `401` — missing, invalid, or expired token; wrong login credentials
- `403` — a non-admin calling an admin route
- `404` — not found, **including another user's character** (existence is not
  leaked)
- `409` — any duplicate or conflict: taken email/nickname, an existing race or
  spell name, a spell already on a character, or deleting reference data that a
  character still uses
- `422` — request-body validation (FastAPI's standard error shape)

Errors are always `{ "detail": "..." }`, except `422`, where `detail` is
FastAPI's array of field errors.

---

## Project layout

```
config.py         env vars, read and validated once at import
database.py       engine, session, get_db dependency
security.py       password hashing, JWT creation
main.py           app, CORS, router wiring, /health
dependencies/     get_current_user / get_current_admin
models/           SQLAlchemy ORM models
schemas/          Pydantic request and response schemas
routers/          one module per resource
alembic/          migrations
seed/             reference data loaders (`python -m seed`)
tests/            pytest suite (needs a live test database)
```

## Adding a migration

```bash
uv run alembic revision --autogenerate -m "what changed"
uv run alembic upgrade head
```

Review the generated file before committing — autogenerate does not always get
constraints right. Remember to run `upgrade head` against the **test** database
too, or the suite will fail against a stale schema.
