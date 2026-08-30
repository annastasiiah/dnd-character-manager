import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database import get_db
from main import app
from models.race import Race
from models.user import User
from security import hash_password

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://dnd_user:12345@localhost:5432/dnd_manager_test",
)

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(bind=test_engine)


@pytest.fixture
def db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.rollback()

        db.execute(text("DELETE FROM characters"))
        db.execute(text("DELETE FROM users"))
        db.execute(text("DELETE FROM races"))

        db.commit()
        db.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_races(db):
    races = [
        Race(
            name="Human",
            description="Test human",
            speed=30,
        ),
        Race(
            name="Elf",
            description="Test elf",
            speed=30,
        ),
    ]

    db.add_all(races)
    db.commit()

    return races


@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        nickname="testuser",
        password_hash=hash_password("password123"),
        role="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def test_admin(db):
    admin = User(
        email="admin@example.com",
        nickname="admin",
        password_hash=hash_password("password123"),
        role="admin",
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin
