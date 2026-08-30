from database import SessionLocal
from models import Race

RACES = [
    {
        "name": "Human",
        "description": "Versatile and ambitious, humans are adaptable and diverse.",
        "speed": 30,
    },
    {
        "name": "Dwarf",
        "description": "Stout and resilient folk known for their endurance and craftsmanship.",
        "speed": 25,
    },
    {
        "name": "Elf",
        "description": "Graceful and long-lived people with keen senses and a natural connection to magic.",
        "speed": 30,
    },
    {
        "name": "Halfling",
        "description": "Small and nimble folk known for their courage, luck, and resourcefulness.",
        "speed": 25,
    },
    {
        "name": "Dragonborn",
        "description": "Proud humanoids descended from dragons, possessing draconic ancestry and breath weapons.",
        "speed": 30,
    },
    {
        "name": "Gnome",
        "description": "Small, clever, and inventive folk with a natural affinity for magic.",
        "speed": 25,
    },
    {
        "name": "Half-Elf",
        "description": "Adaptable people who combine traits of human and elven ancestry.",
        "speed": 30,
    },
    {
        "name": "Half-Orc",
        "description": "Powerful and determined people combining human adaptability with orcish strength.",
        "speed": 30,
    },
    {
        "name": "Tiefling",
        "description": "Humanoids with infernal ancestry, marked by distinctive fiendish traits.",
        "speed": 30,
    },
]


def seed_races():
    db = SessionLocal()

    try:
        for race_data in RACES:
            existing_race = db.query(Race).filter(
                Race.name == race_data["name"]
            ).first()

            if existing_race:
                continue

            db.add(Race(**race_data))

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_races()
    print("Races seeded successfully!")