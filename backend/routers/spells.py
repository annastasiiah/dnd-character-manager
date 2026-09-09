from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_admin
from models.character_spell import CharacterSpell
from models.spell import Spell
from models.user import User
from schemas.spell import (
    SpellCreate,
    SpellListResponse,
    SpellResponse,
    SpellUpdate,
)

router = APIRouter(prefix="/spells", tags=["Spells"])


@router.get("", response_model=SpellListResponse)
def get_spells(
    db: Session = Depends(get_db),
    level: int | None = Query(None, ge=0, le=9),
    school: str | None = None,
    search: str | None = Query(None, min_length=1, max_length=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(Spell)

    if level is not None:
        query = query.filter(Spell.level == level)

    if school:
        query = query.filter(Spell.school.ilike(school))

    if search:
        query = query.filter(Spell.name.ilike(f"%{search}%"))

    total = query.count()

    items = query.order_by(Spell.id).offset(offset).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{spell_id}", response_model=SpellResponse)
def get_spell(spell_id: int, db: Session = Depends(get_db)):
    spell = db.query(Spell).where(Spell.id == spell_id).first()

    if not spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spell not found"
        )

    return spell


@router.post(
    "",
    response_model=SpellResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_spell(
    spell_data: SpellCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    existing_spell = db.query(Spell).filter(Spell.name == spell_data.name).first()

    if existing_spell:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Spell already exists",
        )

    new_spell = Spell(
        name=spell_data.name,
        level=spell_data.level,
        school=spell_data.school,
        casting_time=spell_data.casting_time,
        spell_range=spell_data.spell_range,
        duration=spell_data.duration,
        description=spell_data.description,
    )

    db.add(new_spell)
    db.commit()
    db.refresh(new_spell)

    return new_spell


@router.patch("/{spell_id}", response_model=SpellResponse)
def edit_spell(
    spell_id: int,
    spell_update: SpellUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    spell = db.query(Spell).where(Spell.id == spell_id).first()

    if not spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spell not found"
        )

    update_data = spell_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    if "name" in update_data:
        existing_spell = (
            db.query(Spell)
            .filter(Spell.name == update_data["name"], Spell.id != spell_id)
            .first()
        )

        if existing_spell:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Spell already exists",
            )

    for field, value in update_data.items():
        setattr(spell, field, value)

    db.commit()
    db.refresh(spell)

    return spell


@router.delete("/{spell_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spell(
    spell_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    spell = db.query(Spell).where(Spell.id == spell_id).first()

    if not spell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spell not found"
        )

    in_use = (
        db.query(CharacterSpell).filter(CharacterSpell.spell_id == spell_id).first()
    )

    if in_use:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Spell is known by a character",
        )

    db.delete(spell)
    db.commit()
