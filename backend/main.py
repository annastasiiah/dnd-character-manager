from fastapi import Depends, FastAPI, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.user import User
from models.character import Character
from models.race import Race

from schemas.user import UserCreate, UserResponse
from security import hash_password


from database import get_db

app = FastAPI()

@app.get("/db")
def test_db(db: Session = Depends(get_db)):
    row = db.execute(text(('SELECT 1')))
    return {'result': row.scalar()}

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

