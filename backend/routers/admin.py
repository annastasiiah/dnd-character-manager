from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_admin
from models.user import User
from schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/admin/users", response_model=list[UserResponse])
def get_all_users(
    current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return users


@router.get("/admin/users/{user_id}", response_model=UserResponse)
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


@router.patch("/admin/users/{user_id}", response_model=UserResponse)
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


@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
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
