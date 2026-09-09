from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_admin
from models.character import Character
from models.character_class import CharacterClass
from models.user import User
from schemas.character_class import (
    CharacterClassCreate,
    CharacterClassResponse,
    CharacterClassUpdate,
)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("", response_model=list[CharacterClassResponse])
def get_classes(db: Session = Depends(get_db)):
    return db.query(CharacterClass).order_by(CharacterClass.id).all()


@router.get("/{class_id}", response_model=CharacterClassResponse)
def get_class(class_id: int, db: Session = Depends(get_db)):
    character_class = (
        db.query(CharacterClass).where(CharacterClass.id == class_id).first()
    )

    if not character_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
        )

    return character_class


@router.post(
    "",
    response_model=CharacterClassResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_class(
    class_data: CharacterClassCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    existing_class = (
        db.query(CharacterClass).filter(CharacterClass.name == class_data.name).first()
    )

    if existing_class:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Class already exists",
        )

    new_class = CharacterClass(name=class_data.name)

    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return new_class


@router.patch("/{class_id}", response_model=CharacterClassResponse)
def edit_class(
    class_id: int,
    class_update: CharacterClassUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    character_class = (
        db.query(CharacterClass).where(CharacterClass.id == class_id).first()
    )

    if not character_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
        )

    update_data = class_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    if "name" in update_data:
        existing_class = (
            db.query(CharacterClass)
            .filter(
                CharacterClass.name == update_data["name"],
                CharacterClass.id != class_id,
            )
            .first()
        )

        if existing_class:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Class already exists",
            )

    for field, value in update_data.items():
        setattr(character_class, field, value)

    db.commit()
    db.refresh(character_class)

    return character_class


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    character_class = (
        db.query(CharacterClass).where(CharacterClass.id == class_id).first()
    )

    if not character_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
        )

    in_use = db.query(Character).filter(Character.class_id == class_id).first()

    if in_use:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Class is in use by a character",
        )

    db.delete(character_class)
    db.commit()
