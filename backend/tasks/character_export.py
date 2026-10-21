import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from celery_app import celery_app
from database import SessionLocal
from exporting.character_pdf import generate_character_pdf
from models import Character, CharacterExport


@celery_app.task(bind=True, name="tasks.character_export.export_character_pdf")
def export_character_pdf(self, character_id: int, user_id: int) -> str:
    task_id = self.request.id

    try:
        with SessionLocal() as db:
            export = db.scalar(
                select(CharacterExport).where(CharacterExport.task_id == task_id)
            )

            if export is None:
                raise ValueError("Export record not found")

            statement = (
                select(Character)
                .where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
                .options(
                    selectinload(Character.race),
                    selectinload(Character.character_class),
                    selectinload(Character.background),
                    selectinload(Character.spells),
                )
            )

            character = db.scalar(statement)

            if character is None:
                raise ValueError("Character not found for this user")

            character_data = {
                "name": character.name,
                "level": character.level,
                "race": character.race.name,
                "character_class": character.character_class.name,
                "background": character.background.name,
                "strength": character.strength,
                "dexterity": character.dexterity,
                "constitution": character.constitution,
                "intelligence": character.intelligence,
                "wisdom": character.wisdom,
                "charisma": character.charisma,
                "spells": [
                    {
                        "name": spell.name,
                        "level": spell.level,
                        "school": spell.school,
                        "casting_time": spell.casting_time,
                        "spell_range": spell.spell_range,
                        "duration": spell.duration,
                        "description": spell.description,
                    }
                    for spell in character.spells
                ],
            }

        exports_dir = Path(os.getenv("EXPORTS_DIR", "exports"))
        exports_dir.mkdir(parents=True, exist_ok=True)

        filename = f"character_{character_id}_{task_id}.pdf"
        file_path = exports_dir / filename
        file_path.write_bytes(generate_character_pdf(character_data))

        with SessionLocal() as db:
            export = db.scalar(
                select(CharacterExport).where(CharacterExport.task_id == task_id)
            )
            if export is None:
                raise ValueError("Export record not found")

            export.status = "SUCCESS"
            export.filename = filename
            export.error = None
            db.commit()

        return filename

    except Exception as exc:
        with SessionLocal() as db:
            export = db.scalar(
                select(CharacterExport).where(CharacterExport.task_id == task_id)
            )
            if export is not None:
                export.status = "FAILURE"
                export.error = str(exc)[:2000]
                db.commit()

        raise
