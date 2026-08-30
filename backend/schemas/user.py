from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime
from enum import Enum

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

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    nickname: str | None = Field(None, min_length=1, max_length=50)
    role: UserRole | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
