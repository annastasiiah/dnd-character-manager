
from pathlib import Path

from exporting.character_pdf import generate_character_pdf

character = {
    "name": "Test Wizard",
    "level": 3,
    "race": "Elf",
    "character_class": "Wizard",
    "background": "Sage",
    "strength": 8,
    "dexterity": 14,
    "constitution": 12,
    "intelligence": 17,
    "wisdom": 13,
    "charisma": 10,
    "spells": [
        {
            "name": "Fire Bolt",
            "level": 0,
            "school": "Evocation",
            "casting_time": "1 action",
            "spell_range": "120 feet",
            "duration": "Instantaneous",
            "description": "You hurl a mote of fire at a creature.",
        },
    ],
}

pdf_bytes = generate_character_pdf(character)

Path("test_character.pdf").write_bytes(pdf_bytes)

print(f"PDF generated: {len(pdf_bytes)} bytes")