from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from pydantic import EmailStr

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