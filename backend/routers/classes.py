from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.character_class import CharacterClass
from schemas.character_class import CharacterClassResponse

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("/", response_model=list[CharacterClassResponse])
def get_classes(db: Session = Depends(get_db)):
    return db.query(CharacterClass).all()

