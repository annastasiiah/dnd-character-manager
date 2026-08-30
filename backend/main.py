from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_admin, get_current_user
from models.character import Character
from models.race import Race
from models.user import User
from routers import auth
from schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate
from schemas.user import UserResponse, UserUpdate

app = FastAPI()
app.include_router(auth.router)

# =========================
# ADMIN
# =========================


@app.get("/admin/users", response_model=list[UserResponse])
def get_all_users(
    current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return users


@app.get("/admin/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):  
    user = db.query(User).where(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@app.patch("/admin/users/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    user_update: UserUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .where(
            User.id == user_id,
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    if "email" in update_data:
        existing_user = (
            db.query(User)
            .filter(User.email == update_data["email"], User.id != user_id)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

    if "nickname" in update_data:
        existing_nickname = (
            db.query(User)
            .filter(User.nickname == update_data["nickname"], User.id != user_id)
            .first()
        )

        if existing_nickname:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this nickname already exists",
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@app.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    user = db.query(User).where(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()


# =========================
# CHARACTERS
# =========================


@app.post("/characters", response_model=CharacterResponse)
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


@app.get("/characters", response_model=list[CharacterResponse])
def get_characters(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):

    characters = db.query(Character).filter(Character.user_id == current_user.id).all()

    return characters


@app.get("/characters/{character_id}", response_model=CharacterResponse)
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


@app.patch("/characters/{character_id}", response_model=CharacterResponse)
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


@app.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
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


# =========================
# RACES
# =========================


@app.get("/races")
def get_races(db: Session = Depends(get_db)):
    races = db.query(Race).order_by(Race.id).all()

    return races


@app.get("/races/{race_id}")
def get_race(race_id: int, db: Session = Depends(get_db)):
    race = db.query(Race).where(Race.id == race_id).first()

    if not race:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
        )

    return race
