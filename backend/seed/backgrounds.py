from database import SessionLocal
from models import CharacterBackground


BACKGROUNDS = [
    {"name": "Acolyte"},
    {"name": "Charlatan"},
    {"name": "Criminal"},
    {"name": "Entertainer"},
    {"name": "Folk Hero"},
    {"name": "Guild Artisan"},
    {"name": "Hermit"},
    {"name": "Noble"},
    {"name": "Outlander"},
    {"name": "Sage"},
    {"name": "Sailor"},
    {"name": "Soldier"},
]


def seed_backgrounds():
    db = SessionLocal()

    try:
        for background_data in BACKGROUNDS:
            existing_background = (
                db.query(CharacterBackground)
                .filter(
                    CharacterBackground.name == background_data["name"]
                )
                .first()
            )

            if existing_background:
                continue

            db.add(CharacterBackground(**background_data))

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_backgrounds()
    print("Backgrounds seeded successfully!")