from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.background import CharacterBackground
from schemas.background import CharacterBackgroundResponse

router = APIRouter(prefix="/backgrounds", tags=["Backgrounds"])

@router.get("/", response_model=list[CharacterBackgroundResponse])
def get_backgrounds(db: Session = Depends(get_db)):
    return db.query(CharacterBackground).all()
