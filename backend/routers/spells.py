from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.spell import Spell
from schemas.spell import SpellResponse, SpellCreate
from dependencies.auth import get_current_admin
from models.user import User

router = APIRouter()

@router.get("/spells", response_model=list[SpellResponse])
def get_spells(db: Session = Depends(get_db)):
    spells = db.query(Spell).order_by(Spell.id).all()
    return spells

@router.post(
    "/spells",
    response_model=SpellResponse,
)
def create_spell(
    spell_data: SpellCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    existing_spell = (
        db.query(Spell)
        .filter(Spell.name == spell_data.name)
        .first()
    )

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