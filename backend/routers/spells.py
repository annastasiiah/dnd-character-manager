from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.spell import Spell
from schemas.spell import SpellResponse

router = APIRouter()

@router.get("/spells", response_model=list[SpellResponse])
def get_spells(db: Session = Depends(get_db)):
    spells = db.query(Spell).order_by(Spell.id).all()
    return spells