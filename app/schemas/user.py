from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
