from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_user
from models.character import Character
from models.race import Race
from models.user import User
from schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate

router = APIRouter()


@router.post("/characters", response_model=CharacterResponse)
def create_character(
    character: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    race = db.query(Race).filter(Race.id == character.race_id).first()

    if not race:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
        )

    new_character = Character(
        name=character.name,
        race_id=character.race_id,
        level=character.level,
        strength=character.strength,
        dexterity=character.dexterity,
        constitution=character.constitution,
        intelligence=character.intelligence,
        wisdom=character.wisdom,
        charisma=character.charisma,
        user_id=current_user.id,
    )

    db.add(new_character)
    db.commit()
    db.refresh(new_character)

    return new_character


@router.get("/characters", response_model=list[CharacterResponse])
def get_characters(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):

    characters = db.query(Character).filter(Character.user_id == current_user.id).all()

    return characters


@router.get("/characters/{character_id}", response_model=CharacterResponse)
def get_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    character = (
        db.query(Character)
        .where(Character.id == character_id, Character.user_id == current_user.id)
        .first()
    )

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
        )

    return character


@router.patch("/characters/{character_id}", response_model=CharacterResponse)
def edit_character(
    character_id: int,
    character_update: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    character = (
        db.query(Character)
        .where(Character.id == character_id, Character.user_id == current_user.id)
        .first()
    )

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
        )

    update_data = character_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    if "race_id" in update_data:
        race = db.query(Race).filter(Race.id == update_data["race_id"]).first()
        if not race:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
            )

    for field, value in update_data.items():
        setattr(character, field, value)

    db.commit()
    db.refresh(character)

    return character


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    character = (
        db.query(Character)
        .where(Character.id == character_id, Character.user_id == current_user.id)
        .first()
    )

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
        )

    db.delete(character)
    db.commit()
