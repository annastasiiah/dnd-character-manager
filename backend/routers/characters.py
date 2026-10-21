import os
from pathlib import Path
from uuid import uuid4

from celery.exceptions import OperationalError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, selectinload

from database import get_db
from dependencies.auth import get_current_user
from models.background import CharacterBackground
from models.character import Character
from models.character_class import CharacterClass
from models.character_export import CharacterExport
from models.character_spell import CharacterSpell
from models.race import Race
from models.spell import Spell
from models.user import User
from schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate
from schemas.spell import CharacterSpellCreate, SpellResponse
from tasks.character_export import export_character_pdf

router = APIRouter(prefix="/characters", tags=["Characters"])


def _character_query(db: Session):
    """Base query that eager-loads everything `CharacterResponse` expands,
    so listing characters stays a fixed number of round trips."""
    return db.query(Character).options(
        selectinload(Character.race),
        selectinload(Character.character_class),
        selectinload(Character.background),
    )


def _get_owned_character(character_id: int, user: User, db: Session) -> Character:
    character = (
        _character_query(db)
        .where(Character.id == character_id, Character.user_id == user.id)
        .first()
    )

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
        )

    return character

@router.post(
    "/{character_id}/export",
    status_code=status.HTTP_202_ACCEPTED,
)
def request_character_export(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_character(character_id, current_user, db)

    task_id = str(uuid4())

    export = CharacterExport(
        task_id=task_id,
        character_id=character_id,
        user_id=current_user.id,
        status="PENDING",
    )

    db.add(export)
    db.commit()

    try:
        export_character_pdf.apply_async(
            kwargs={
                "character_id": character_id,
                "user_id": current_user.id,
            },
            task_id=task_id,
        )
    except OperationalError:
        export.status = "FAILURE"
        export.error = "Failed to enqueue export task"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not start PDF export",
        )

    return {
        "task_id": task_id,
        "status": "PENDING",
    }

@router.get("/exports/{task_id}")
def get_character_export_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    export = (
        db.query(CharacterExport)
        .filter(
            CharacterExport.task_id == task_id,
            CharacterExport.user_id == current_user.id,
        )
        .first()
    )

    if export is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )

    return {
        "task_id": export.task_id,
        "character_id": export.character_id,
        "status": export.status,
        "created_at": export.created_at,
        "updated_at": export.updated_at,
        "error": (
            "PDF export failed"
            if export.status == "FAILURE"
            else None
        ),
    }


@router.get("/exports/{task_id}/download")
def download_character_export(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    export = (
        db.query(CharacterExport)
        .filter(
            CharacterExport.task_id == task_id,
            CharacterExport.user_id == current_user.id,
        )
        .first()
    )

    if export is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )

    if export.status != "SUCCESS" or not export.filename:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Export is not ready for download",
        )

    exports_dir = Path(os.getenv("EXPORTS_DIR", "exports")).resolve()

    if Path(export.filename).name != export.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid export filename",
        )

    file_path = (exports_dir / export.filename).resolve()

    if file_path.parent != exports_dir or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=export.filename,
    )

@router.post(
    "",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_character(
    character: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    race = db.query(Race).filter(Race.id == character.race_id).first()

    if not race:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
        )

    class_ = (
        db.query(CharacterClass).filter(CharacterClass.id == character.class_id).first()
    )

    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character class not found",
        )

    background = (
        db.query(CharacterBackground)
        .filter(CharacterBackground.id == character.background_id)
        .first()
    )

    if not background:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Background not found",
        )

    new_character = Character(
        name=character.name,
        race_id=character.race_id,
        class_id=character.class_id,
        background_id=character.background_id,
        level=character.level,
        strength=character.strength,
        dexterity=character.dexterity,
        constitution=character.constitution,
        intelligence=character.intelligence,
        wisdom=character.wisdom,
        charisma=character.charisma,
        user_id=current_user.id,
    )

    db.add(new_character)
    db.commit()
    db.refresh(new_character)

    return new_character


@router.get("", response_model=list[CharacterResponse])
def get_characters(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    characters = (
        _character_query(db)
        .filter(Character.user_id == current_user.id)
        .order_by(Character.id)
        .all()
    )

    return characters


@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_owned_character(character_id, current_user, db)


@router.patch("/{character_id}", response_model=CharacterResponse)
def edit_character(
    character_id: int,
    character_update: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    character = _get_owned_character(character_id, current_user, db)

    update_data = character_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    if "class_id" in update_data:
        charclass = (
            db.query(CharacterClass)
            .filter(CharacterClass.id == update_data["class_id"])
            .first()
        )

        if not charclass:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
            )

    if "race_id" in update_data:
        race = db.query(Race).filter(Race.id == update_data["race_id"]).first()

        if not race:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
            )

    if "background_id" in update_data:
        background = (
            db.query(CharacterBackground)
            .filter(CharacterBackground.id == update_data["background_id"])
            .first()
        )

        if not background:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Background not found"
            )

    for field, value in update_data.items():
        setattr(character, field, value)

    db.commit()
    db.refresh(character)

    return character


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    character = _get_owned_character(character_id, current_user, db)

    db.delete(character)
    db.commit()


@router.get("/{character_id}/spells", response_model=list[SpellResponse])
def get_character_spells(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_character(character_id, current_user, db)

    spells = (
        db.query(Spell)
        .join(CharacterSpell, CharacterSpell.spell_id == Spell.id)
        .filter(CharacterSpell.character_id == character_id)
        .order_by(Spell.id)
        .all()
    )

    return spells


@router.post(
    "/{character_id}/spells",
    response_model=SpellResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_spell(
    character_id: int,
    spell_data: CharacterSpellCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_character(character_id, current_user, db)

    spell = db.query(Spell).where(Spell.id == spell_data.spell_id).first()

    if not spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spell not found",
        )

    character_spell = (
        db.query(CharacterSpell)
        .where(
            CharacterSpell.character_id == character_id,
            CharacterSpell.spell_id == spell_data.spell_id,
        )
        .first()
    )

    if character_spell:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Spell already added to character",
        )

    db.add(
        CharacterSpell(
            character_id=character_id,
            spell_id=spell_data.spell_id,
        )
    )
    db.commit()

    return spell


@router.delete(
    "/{character_id}/spells/{spell_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_spell(
    character_id: int,
    spell_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_character(character_id, current_user, db)

    spell = db.query(Spell).where(Spell.id == spell_id).first()

    if not spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spell not found",
        )

    character_spell = (
        db.query(CharacterSpell)
        .where(
            CharacterSpell.character_id == character_id,
            CharacterSpell.spell_id == spell_id,
        )
        .first()
    )

    if not character_spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spell not found for this character",
        )

    db.delete(character_spell)
    db.commit()
