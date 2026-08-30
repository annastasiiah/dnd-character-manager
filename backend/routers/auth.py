from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import TokenResponse, UserCreate, UserResponse
from security import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post(
    "/users/registration",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    existing_nickname = db.query(User).filter(User.nickname == user.nickname).first()

    if existing_nickname:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this nickname already exists",
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        email=user.email,
        nickname=user.nickname,
        password_hash=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/users/login", response_model=TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    existing_login = db.query(User).filter(User.email == form_data.username).first()

    if not existing_login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(
        form_data.password,
        existing_login.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(
        data={
            "sub": str(existing_login.id),
            "role": existing_login.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
