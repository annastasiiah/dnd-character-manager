from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from schemas.patch import PatchModel


class UserCreate(BaseModel):
    email: EmailStr
    nickname: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserUpdate(PatchModel):
    """Admin-side edit. An admin may reset a password without knowing it."""

    non_nullable_fields = frozenset({"email", "nickname", "role", "password"})

    email: EmailStr | None = None
    nickname: str | None = Field(None, min_length=1, max_length=50)
    role: UserRole | None = None
    password: str | None = Field(None, min_length=8)


class UserSelfUpdate(PatchModel):
    """Fields a user may change on their own account. Deliberately has no
    `role`, so a user cannot promote themselves via PATCH /users/me."""

    non_nullable_fields = frozenset({"email", "nickname", "password"})

    email: EmailStr | None = None
    nickname: str | None = Field(None, min_length=1, max_length=50)
    password: str | None = Field(None, min_length=8)
    current_password: str | None = None

    @model_validator(mode="after")
    def current_password_required_to_change_password(self):
        if self.password is not None and not self.current_password:
            raise ValueError("current_password is required to change the password")

        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
