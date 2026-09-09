from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_admin
from models.background import CharacterBackground
from models.character import Character
from models.user import User
from schemas.background import (
    CharacterBackgroundCreate,
    CharacterBackgroundResponse,
    CharacterBackgroundUpdate,
)

router = APIRouter(prefix="/backgrounds", tags=["Backgrounds"])


@router.get("", response_model=list[CharacterBackgroundResponse])
def get_backgrounds(db: Session = Depends(get_db)):
    return db.query(CharacterBackground).order_by(CharacterBackground.id).all()


@router.get("/{background_id}", response_model=CharacterBackgroundResponse)
def get_background(background_id: int, db: Session = Depends(get_db)):
    background = (
        db.query(CharacterBackground)
        .where(CharacterBackground.id == background_id)
        .first()
    )

    if not background:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Background not found"
        )

    return background


@router.post(
    "",
    response_model=CharacterBackgroundResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_background(
    background_data: CharacterBackgroundCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    existing_background = (
        db.query(CharacterBackground)
        .filter(CharacterBackground.name == background_data.name)
        .first()
    )

    if existing_background:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Background already exists",
        )

    new_background = CharacterBackground(name=background_data.name)

    db.add(new_background)
    db.commit()
    db.refresh(new_background)

    return new_background


@router.patch("/{background_id}", response_model=CharacterBackgroundResponse)
def edit_background(
    background_id: int,
    background_update: CharacterBackgroundUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    background = (
        db.query(CharacterBackground)
        .where(CharacterBackground.id == background_id)
        .first()
    )

    if not background:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Background not found"
        )

    update_data = background_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    if "name" in update_data:
        existing_background = (
            db.query(CharacterBackground)
            .filter(
                CharacterBackground.name == update_data["name"],
                CharacterBackground.id != background_id,
            )
            .first()
        )

        if existing_background:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Background already exists",
            )

    for field, value in update_data.items():
        setattr(background, field, value)

    db.commit()
    db.refresh(background)

    return background


@router.delete("/{background_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_background(
    background_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    background = (
        db.query(CharacterBackground)
        .where(CharacterBackground.id == background_id)
        .first()
    )

    if not background:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Background not found"
        )

    in_use = (
        db.query(Character).filter(Character.background_id == background_id).first()
    )

    if in_use:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Background is in use by a character",
        )

    db.delete(background)
    db.commit()
