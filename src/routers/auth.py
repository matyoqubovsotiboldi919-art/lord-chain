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
from src.schemas.auth import LoginRequest, OTPVerifyRequest
from src.schemas.token import Token

from src.services.security import hash_password, verify_password, create_access_token
from src.services.otp import issue_otp, verify_otp
from src.services.email import send_otp_email
from src.services.audit import audit_log
from src.services.sessions import set_single_session

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _is_locked(user: User) -> bool:
    # ✅ DB ustuni: lock_until
    return bool(user.lock_until and user.lock_until > _utcnow())


def _lock_user(user: User, minutes: int = 60) -> None:
    # ✅ DB ustuni: lock_until, failed_login_attempts
    user.lock_until = _utcnow() + timedelta(minutes=minutes)
    user.failed_login_attempts = 0


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    email = payload.email.lower().strip()

    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    address = f"LORD_{uuid4().hex}"

    # ✅ MUHIM: User modelida aniq shu nomlar bo‘lishi kerak:
    # password_hash, address, balance, failed_login_attempts, lock_until
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

    audit_log(
        db,
        actor=email,
        action="REGISTER",
        entity="users",
        entity_id=str(user.id),
        meta={"address": address},
    )
    return user


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
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

    # ✅ success reset
    user.failed_login_attempts = 0
    user.lock_until = None
    db.commit()

    otp_rec = issue_otp(db, user.id)
    send_otp_email(to_email=user.email, otp=otp_rec.code)

    audit_log(db, actor=email, action="LOGIN_OK_OTP_SENT", entity="users", entity_id=str(user.id))
    return {"detail": "OTP sent. Use /api/v1/auth/verify-otp"}


@router.post("/verify-otp", response_model=Token)
def verify_otp_route(payload: OTPVerifyRequest, db: Session = Depends(get_db)) -> Token:
    email = payload.email.lower().strip()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    if user.is_frozen:
        raise HTTPException(status_code=403, detail="Account is frozen")

    if _is_locked(user):
        raise HTTPException(status_code=403, detail="Account is locked. Try later.")

    ok = verify_otp(db, user.id, payload.otp)
    if not ok:
        user.failed_login_attempts = int(user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= 3:
            _lock_user(user, minutes=60)
        db.commit()
        audit_log(db, actor=email, action="OTP_FAIL", entity="users", entity_id=str(user.id))
        raise HTTPException(status_code=401, detail="Invalid OTP")

    # ✅ OTP ok
    user.failed_login_attempts = 0
    user.lock_until = None
    db.commit()

    # ✅ single active session
    session_id = set_single_session(db, user.id)

    # JWT config (env dan olamiz)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

    # ✅ create_access_token (bizning security.py dagi yangi formatga mos)
    token_str = create_access_token(
        subject=user.email,
        secret_key=JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
        expires_minutes=JWT_EXPIRE_MINUTES,
        extra_claims={"sid": session_id},
    )

    audit_log(
        db,
        actor=email,
        action="OTP_OK_TOKEN",
        entity="users",
        entity_id=str(user.id),
        meta={"sid": session_id},
    )
    return Token(access_token=token_str, token_type="bearer")