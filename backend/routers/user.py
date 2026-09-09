from fastapi import APIRouter, Depends, HTTPException, status
from dependencies.auth import get_current_user
from models.user import User
from schemas.user import UserResponse, UserSelfUpdate
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):

    return current_user

@router.patch("/users/me", response_model=UserResponse)
def edit_me(
    user_update: UserSelfUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = current_user
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    if "email" in update_data:
        existing_user = (
            db.query(User)
            .filter(
                User.email == update_data["email"],
                User.id != user.id,
            )
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
            .filter(
                User.nickname == update_data["nickname"],
                User.id != user.id,
            )
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