from database import SessionLocal
from models import CharacterClass

CLASSES = [
    {
        "name": "Barbarian",
        "description": "A fierce warrior who channels primal rage to withstand damage and strike with overwhelming force.",
        "primary_ability": "Strength",
        "hit_die": "d12",
    },
    {
        "name": "Bard",
        "description": "A versatile performer whose magic draws on music, words, creativity, and inspiration.",
        "primary_ability": "Charisma",
        "hit_die": "d8",
    },
    {
        "name": "Cleric",
        "description": "A divine spellcaster who channels the power of a deity to protect allies and overcome enemies.",
        "primary_ability": "Wisdom",
        "hit_die": "d8",
    },
    {
        "name": "Druid",
        "description": "A guardian of nature who commands natural magic and can transform into animal forms.",
        "primary_ability": "Wisdom",
        "hit_die": "d8",
    },
    {
        "name": "Fighter",
        "description": "A skilled combatant trained to master weapons, armor, and a wide range of battle tactics.",
        "primary_ability": "Strength or Dexterity",
        "hit_die": "d10",
    },
    {
        "name": "Monk",
        "description": "A disciplined martial artist who harnesses inner energy to enhance movement and unarmed combat.",
        "primary_ability": "Dexterity and Wisdom",
        "hit_die": "d8",
    },
    {
        "name": "Paladin",
        "description": "A holy warrior bound by a sacred oath, combining martial prowess with divine magic.",
        "primary_ability": "Strength and Charisma",
        "hit_die": "d10",
    },
    {
        "name": "Ranger",
        "description": "A wilderness expert who combines combat skills, survival instincts, and nature-based magic.",
        "primary_ability": "Dexterity and Wisdom",
        "hit_die": "d10",
    },
    {
        "name": "Rogue",
        "description": "A cunning specialist who relies on stealth, precision, quick reflexes, and tactical strikes.",
        "primary_ability": "Dexterity",
        "hit_die": "d8",
    },
    {
        "name": "Sorcerer",
        "description": "A spellcaster whose innate magical power comes from an extraordinary origin or bloodline.",
        "primary_ability": "Charisma",
        "hit_die": "d6",
    },
    {
        "name": "Warlock",
        "description": "A wielder of mysterious magic gained through a pact with a powerful otherworldly patron.",
        "primary_ability": "Charisma",
        "hit_die": "d8",
    },
    {
        "name": "Wizard",
        "description": "A scholarly spellcaster who studies arcane principles and builds a versatile repertoire of spells.",
        "primary_ability": "Intelligence",
        "hit_die": "d6",
    },
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
                for field, value in class_data.items():
                    setattr(existing_class, field, value)
            else:
                db.add(CharacterClass(**class_data))

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_classes()
    print("Classes seeded successfully!")