# backend/src/routers/auth.py
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserOut
from src.schemas.auth import LoginRequest
from src.schemas.token import Token

from src.services.security import hash_password, verify_password, create_access_token
from src.services.audit import audit_log
from src.services.sessions import set_single_session

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _is_locked(user: User) -> bool:
    return bool(user.lock_until and user.lock_until > _utcnow())


def _lock_user(user: User, minutes: int = 60) -> None:
    user.lock_until = _utcnow() + timedelta(minutes=minutes)
    user.failed_login_attempts = 0


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    email = payload.email.lower().strip()

    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    address = f"LORD_{uuid4().hex}"

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        address=address,
        balance="1000.00000000",
        is_active=True,
        is_frozen=False,
        failed_login_attempts=0,
        lock_until=None,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    audit_log(db, actor=email, action="REGISTER", entity="users", entity_id=str(user.id), meta={"address": address})
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    email = payload.email.lower().strip()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_frozen:
        raise HTTPException(status_code=403, detail="Account is frozen")

    if _is_locked(user):
        raise HTTPException(status_code=403, detail="Account is locked. Try later.")

    if not verify_password(payload.password, user.password_hash):
        user.failed_login_attempts = int(user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= 3:
            _lock_user(user, minutes=60)
        db.commit()
        audit_log(db, actor=email, action="LOGIN_FAIL", entity="users", entity_id=str(user.id))
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # success reset
    user.failed_login_attempts = 0
    user.lock_until = None
    db.commit()

    # single active session
    session_id = set_single_session(db, user.id)

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

    token_str = create_access_token(
        subject=user.email,
        secret_key=JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
        expires_minutes=JWT_EXPIRE_MINUTES,
        extra_claims={"sid": session_id},
    )

    audit_log(db, actor=email, action="LOGIN_OK_TOKEN", entity="users", entity_id=str(user.id), meta={"sid": session_id})
    return Token(access_token=token_str, token_type="bearer")