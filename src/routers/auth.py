from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.models import User

from src.services.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# -------------------- Schemas (local, xato chiqmasin deb) --------------------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------------------- Endpoints --------------------
@router.post("/register", status_code=200)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=email,
        hashed_password=get_password_hash(payload.password),
        # Agar modelda boshqa required field bo‘lsa, shu yerga qo‘shib qo‘ying.
        # masalan: is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "registered"}


@router.post("/login", response_model=TokenOut, status_code=200)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ MUHIM: /users/me 401 bo‘lmasligi uchun JWT ichida sub DOIM bo‘lsin
    token = create_access_token(subject=user.email)

    return {"access_token": token, "token_type": "bearer"}