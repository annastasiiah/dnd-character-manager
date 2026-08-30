from fastapi import Depends, FastAPI, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    hash_password,
    verify_password,
)
from models.user import User
from models.character import Character
from models.race import Race

from schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from schemas.character import CharacterCreate, CharacterResponse
from security import hash_password, verify_password, create_access_token

from database import get_db

app = FastAPI()

@app.post("/users/registration", 
        response_model = UserResponse, 
        status_code = status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
        ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    existing_nickname = db.query(User).filter(
        User.nickname == user.nickname
        ).first()
    
    if existing_nickname:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this nickname already exists"
        )
    
    hashed_password = hash_password(user.password)

    new_user = User(
        email = user.email,
        nickname = user.nickname,
        password_hash = hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/users/login", response_model=TokenResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):

    existing_login = db.query(User).filter(
        User.email == user.email
        ).first()

    if not existing_login:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
    
    if not verify_password(user.password, existing_login.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
            )
    
    access_token = create_access_token(
        data={
            "sub": str(existing_login.id),
            "role": existing_login.role
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    current_user = db.query(User).filter(
        User.id == user_id
        ).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return current_user

@app.post("/characters", response_model=CharacterResponse)
def create_character(
    character: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    race = db.query(Race).filter(
            Race.id == character.race_id
            ).first()
    
    if not race:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Race not found"
        )
    
    new_character = Character(
        name = character.name,
        race_id = character.race_id,
        level = character.level,
        strength = character.strength,
        dexterity = character.dexterity,
        constitution = character.constitution,
        intelligence = character.intelligence,
        wisdom = character.wisdom,
        charisma = character.charisma,
        user_id = current_user.id
    )


    db.add(new_character)
    db.commit()
    db.refresh(new_character)
    
    return new_character

@app.get("/characters", response_model = list[CharacterResponse])
def get_characters(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):

    characters = db.query(Character).filter(
        Character.user_id == current_user.id
        ).all()
    
    return characters