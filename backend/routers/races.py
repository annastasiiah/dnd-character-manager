from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.race import Race
from schemas.race import RaceResponse, RaceCreate
from dependencies.auth import get_current_admin
from models.user import User

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

@router.post(
    "/races",
    response_model=RaceResponse,
)
def create_race(
    race_data: RaceCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    existing_race = (
        db.query(Race)
        .filter(Race.name == race_data.name)
        .first()
    )

    if existing_race:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Race already exists",
        )
    
    new_race = Race(
        name=race_data.name,
        description=race_data.description,
        speed=race_data.speed
    )

    db.add(new_race)
    db.commit()
    db.refresh(new_race)

    return new_race