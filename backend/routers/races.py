from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_admin
from models.character import Character
from models.race import Race
from models.user import User
from schemas.race import RaceCreate, RaceResponse, RaceUpdate

router = APIRouter(prefix="/races", tags=["Races"])


@router.get("", response_model=list[RaceResponse])
def get_races(db: Session = Depends(get_db)):
    races = db.query(Race).order_by(Race.id).all()

    return races


@router.get("/{race_id}", response_model=RaceResponse)
def get_race(race_id: int, db: Session = Depends(get_db)):
    race = db.query(Race).where(Race.id == race_id).first()

    if not race:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
        )

    return race


@router.post(
    "",
    response_model=RaceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_race(
    race_data: RaceCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    existing_race = db.query(Race).filter(Race.name == race_data.name).first()

    if existing_race:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Race already exists",
        )

    new_race = Race(
        name=race_data.name,
        description=race_data.description,
        speed=race_data.speed,
    )

    db.add(new_race)
    db.commit()
    db.refresh(new_race)

    return new_race


@router.patch("/{race_id}", response_model=RaceResponse)
def edit_race(
    race_id: int,
    race_update: RaceUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    race = db.query(Race).where(Race.id == race_id).first()

    if not race:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
        )

    update_data = race_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    if "name" in update_data:
        existing_race = (
            db.query(Race)
            .filter(Race.name == update_data["name"], Race.id != race_id)
            .first()
        )

        if existing_race:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Race already exists",
            )

    for field, value in update_data.items():
        setattr(race, field, value)

    db.commit()
    db.refresh(race)

    return race


@router.delete("/{race_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_race(
    race_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    race = db.query(Race).where(Race.id == race_id).first()

    if not race:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
        )

    in_use = db.query(Character).filter(Character.race_id == race_id).first()

    if in_use:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Race is in use by a character",
        )

    db.delete(race)
    db.commit()
