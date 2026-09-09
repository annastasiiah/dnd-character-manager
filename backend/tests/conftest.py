import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database import get_db
from main import app
from models.background import CharacterBackground
from models.character_class import CharacterClass
from models.race import Race
from models.spell import Spell
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

        db.execute(text("DELETE FROM character_spells"))
        db.execute(text("DELETE FROM characters"))
        db.execute(text("DELETE FROM users"))
        db.execute(text("DELETE FROM spells"))
        db.execute(text("DELETE FROM races"))
        db.execute(text("DELETE FROM classes"))
        db.execute(text("DELETE FROM backgrounds"))

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


@pytest.fixture
def test_classes(db):
    classes = [
        CharacterClass(name="Wizard"),
        CharacterClass(name="Rogue"),
    ]

    db.add_all(classes)
    db.commit()

    return classes


@pytest.fixture
def test_backgrounds(db):
    backgrounds = [
        CharacterBackground(name="Sage"),
        CharacterBackground(name="Soldier"),
    ]

    db.add_all(backgrounds)
    db.commit()

    return backgrounds


@pytest.fixture
def test_spells(db):
    spells = [
        Spell(
            name="Magic Missile",
            level=1,
            school="Evocation",
            casting_time="1 action",
            spell_range="120 feet",
            duration="Instantaneous",
            description="Three darts of magical force.",
        ),
        Spell(
            name="Shield",
            level=1,
            school="Abjuration",
            casting_time="1 reaction",
            spell_range="Self",
            duration="1 round",
            description="An invisible barrier of magical force.",
        ),
    ]

    db.add_all(spells)
    db.commit()

    return spells


@pytest.fixture
def auth_headers(client, test_user):
    """Bearer headers for `test_user`."""
    response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """Bearer headers for `test_admin`."""
    response = client.post(
        "/users/login",
        data={
            "username": test_admin.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def character_payload(test_races, test_classes, test_backgrounds):
    """A valid POST /characters body wired to the seeded reference rows."""
    return {
        "name": "Arwen",
        "race_id": test_races[0].id,
        "class_id": test_classes[0].id,
        "background_id": test_backgrounds[0].id,
        "level": 5,
        "strength": 10,
        "dexterity": 14,
        "constitution": 12,
        "intelligence": 16,
        "wisdom": 13,
        "charisma": 15,
    }
