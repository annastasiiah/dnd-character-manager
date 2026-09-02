from database import SessionLocal
from models import Spell


SPELLS = [
    {
        "name": "Fire Bolt",
        "level": 0,
        "school": "Evocation",
        "casting_time": "1 action",
        "spell_range": "120 feet",
        "duration": "Instantaneous",
        "description": "You hurl a mote of fire at a creature or object within range.",
    },
    {
        "name": "Mage Hand",
        "level": 0,
        "school": "Conjuration",
        "casting_time": "1 action",
        "spell_range": "30 feet",
        "duration": "1 minute",
        "description": "A spectral hand appears at a point you choose within range.",
    },
    {
        "name": "Light",
        "level": 0,
        "school": "Evocation",
        "casting_time": "1 action",
        "spell_range": "Touch",
        "duration": "1 hour",
        "description": "You touch one object that is no larger than 10 feet in any dimension.",
    },
    {
        "name": "Prestidigitation",
        "level": 0,
        "school": "Transmutation",
        "casting_time": "1 action",
        "spell_range": "10 feet",
        "duration": "Up to 1 hour",
        "description": "You create a minor magical effect or harmless sensory effect.",
    },
    {
        "name": "Cure Wounds",
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 action",
        "spell_range": "Touch",
        "duration": "Instantaneous",
        "description": "A creature you touch regains hit points.",
    },
    {
        "name": "Magic Missile",
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 action",
        "spell_range": "120 feet",
        "duration": "Instantaneous",
        "description": "You create three glowing darts of magical force.",
    },
    {
        "name": "Shield",
        "level": 1,
        "school": "Abjuration",
        "casting_time": "1 reaction",
        "spell_range": "Self",
        "duration": "1 round",
        "description": "An invisible barrier of magical force protects you.",
    },
    {
        "name": "Healing Word",
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 bonus action",
        "spell_range": "60 feet",
        "duration": "Instantaneous",
        "description": "A creature of your choice regains hit points.",
    },
    {
        "name": "Thunderwave",
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 action",
        "spell_range": "Self (15-foot cube)",
        "duration": "Instantaneous",
        "description": "A wave of thunderous force sweeps out from you.",
    },
    {
        "name": "Burning Hands",
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 action",
        "spell_range": "Self (15-foot cone)",
        "duration": "Instantaneous",
        "description": "A thin sheet of flames shoots forth from your hands.",
    },
    {
        "name": "Detect Magic",
        "level": 1,
        "school": "Divination",
        "casting_time": "1 action",
        "spell_range": "Self",
        "duration": "Concentration, up to 10 minutes",
        "description": "You sense the presence of magic within 30 feet of you.",
    },
    {
        "name": "Charm Person",
        "level": 1,
        "school": "Enchantment",
        "casting_time": "1 action",
        "spell_range": "30 feet",
        "duration": "1 hour",
        "description": "You attempt to charm a humanoid you can see within range.",
    },
    {
        "name": "Invisibility",
        "level": 2,
        "school": "Illusion",
        "casting_time": "1 action",
        "spell_range": "Touch",
        "duration": "Concentration, up to 1 hour",
        "description": "A creature you touch becomes invisible.",
    },
    {
        "name": "Misty Step",
        "level": 2,
        "school": "Conjuration",
        "casting_time": "1 bonus action",
        "spell_range": "Self",
        "duration": "Instantaneous",
        "description": "You teleport up to 30 feet to an unoccupied space you can see.",
    },
    {
        "name": "Hold Person",
        "level": 2,
        "school": "Enchantment",
        "casting_time": "1 action",
        "spell_range": "60 feet",
        "duration": "Concentration, up to 1 minute",
        "description": "A humanoid you can see within range must succeed on a Wisdom saving throw or be paralyzed.",
    },
    {
        "name": "Scorching Ray",
        "level": 2,
        "school": "Evocation",
        "casting_time": "1 action",
        "spell_range": "120 feet",
        "duration": "Instantaneous",
        "description": "You create three rays of fire and hurl them at targets within range.",
    },
    {
        "name": "Fireball",
        "level": 3,
        "school": "Evocation",
        "casting_time": "1 action",
        "spell_range": "150 feet",
        "duration": "Instantaneous",
        "description": "A bright streak flashes from your pointing finger and explodes into a fiery blast.",
    },
    {
        "name": "Counterspell",
        "level": 3,
        "school": "Abjuration",
        "casting_time": "1 reaction",
        "spell_range": "60 feet",
        "duration": "Instantaneous",
        "description": "You attempt to interrupt a creature in the process of casting a spell.",
    },
    {
        "name": "Fly",
        "level": 3,
        "school": "Transmutation",
        "casting_time": "1 action",
        "spell_range": "Touch",
        "duration": "Concentration, up to 10 minutes",
        "description": "You touch a willing creature and grant it the ability to fly.",
    },
    {
        "name": "Lightning Bolt",
        "level": 3,
        "school": "Evocation",
        "casting_time": "1 action",
        "spell_range": "Self (100-foot line)",
        "duration": "Instantaneous",
        "description": "A stroke of lightning forming a line blasts out from you.",
    },
]


def seed_spells():
    db = SessionLocal()

    try:
        for spell_data in SPELLS:
            existing_spell = (
                db.query(Spell)
                .filter(Spell.name == spell_data["name"])
                .first()
            )

            if existing_spell:
                continue

            db.add(Spell(**spell_data))

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_spells()
    print("Spells seeded successfully!")