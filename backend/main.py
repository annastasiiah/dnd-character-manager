from fastapi import Depends, FastAPI, status, HTTPException
from sqlalchemy.orm import Session

from models.user import User
from models.character import Character
from models.race import Race

from schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
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