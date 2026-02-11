# backend/src/schemas/user.py
from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    address: str
    balance: float

    class Config:
        from_attributes = True
