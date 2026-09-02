from database import SessionLocal
from models import CharacterClass


CLASSES = [
    {"name": "Barbarian"},
    {"name": "Bard"},
    {"name": "Cleric"},
    {"name": "Druid"},
    {"name": "Fighter"},
    {"name": "Monk"},
    {"name": "Paladin"},
    {"name": "Ranger"},
    {"name": "Rogue"},
    {"name": "Sorcerer"},
    {"name": "Warlock"},
    {"name": "Wizard"},
]


def seed_classes():
    db = SessionLocal()

    try:
        for class_data in CLASSES:
            existing_class = (
                db.query(CharacterClass)
                .filter(CharacterClass.name == class_data["name"])
                .first()
            )

            if existing_class:
                continue

            db.add(CharacterClass(**class_data))

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_classes()
    print("Classes seeded successfully!")