from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.race import Race

router = APIRouter()


@router.get("/races")
def get_races(db: Session = Depends(get_db)):
    races = db.query(Race).order_by(Race.id).all()

    return races


@router.get("/races/{race_id}")
def get_race(race_id: int, db: Session = Depends(get_db)):
    race = db.query(Race).where(Race.id == race_id).first()

    if not race:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
        )

    return race
