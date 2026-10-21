from database import SessionLocal
from models import CharacterBackground

BACKGROUNDS = [
    {
        "name": "Acolyte",
        "description": "You served a temple or religious community, learning sacred traditions and assisting its faithful.",
        "skill_proficiencies": ["Insight", "Religion"],
    },
    {
        "name": "Charlatan",
        "description": "You survived by deception, disguises, and elaborate schemes that let you manipulate appearances.",
        "skill_proficiencies": ["Deception", "Sleight of Hand"],
    },
    {
        "name": "Criminal",
        "description": "You built a life outside the law, gaining experience with illicit networks and underworld dealings.",
        "skill_proficiencies": ["Deception", "Stealth"],
    },
    {
        "name": "Entertainer",
        "description": "You earned a living performing for audiences, captivating crowds with your artistic talents.",
        "skill_proficiencies": ["Acrobatics", "Performance"],
    },
    {
        "name": "Folk Hero",
        "description": "You came from an ordinary community and became known for a deed that made you its champion.",
        "skill_proficiencies": ["Animal Handling", "Survival"],
    },
    {
        "name": "Guild Artisan",
        "description": "You trained in a craft and belong to a guild that provides professional contacts and support.",
        "skill_proficiencies": ["Insight", "Persuasion"],
    },
    {
        "name": "Hermit",
        "description": "You spent a long period in seclusion, pursuing solitude, contemplation, or a personal revelation.",
        "skill_proficiencies": ["Medicine", "Religion"],
    },
    {
        "name": "Noble",
        "description": "You were raised among privilege and influence, familiar with social expectations and high society.",
        "skill_proficiencies": ["History", "Persuasion"],
    },
    {
        "name": "Outlander",
        "description": "You grew up far from settled lands and learned to travel, hunt, and survive in the wilderness.",
        "skill_proficiencies": ["Athletics", "Survival"],
    },
    {
        "name": "Sage",
        "description": "You devoted years to studying ancient knowledge, researching mysteries, and collecting lore.",
        "skill_proficiencies": ["Arcana", "History"],
    },
    {
        "name": "Sailor",
        "description": "You worked aboard a vessel, learning the routines of seafaring life and the challenges of the open water.",
        "skill_proficiencies": ["Athletics", "Perception"],
    },
    {
        "name": "Soldier",
        "description": "You served in an organized military force and learned discipline, teamwork, and battlefield survival.",
        "skill_proficiencies": ["Athletics", "Intimidation"],
    },
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
                for field, value in background_data.items():
                    setattr(existing_background, field, value)
            else:
                db.add(CharacterBackground(**background_data))

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_backgrounds()
    print("Backgrounds seeded successfully!")