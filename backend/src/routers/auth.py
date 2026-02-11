# backend/src/routers/auth.py
from __future__ import annotations

from datetime import datetime, timedelta
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


def _is_locked(user: User) -> bool:
    return bool(user.locked_until and user.locked_until > datetime.utcnow())


def _lock_user(user: User, minutes: int = 60):
    user.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
    user.failed_attempts = 0


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
        failed_attempts=0,
        locked_until=None,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    audit_log(db, actor=email, action="REGISTER", entity="users", entity_id=str(user.id), meta={"address": address})
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
        user.failed_attempts = int(user.failed_attempts or 0) + 1
        if user.failed_attempts >= 3:
            _lock_user(user, minutes=60)
        db.commit()
        audit_log(db, actor=email, action="LOGIN_FAIL", entity="users", entity_id=str(user.id))
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # success reset
    user.failed_attempts = 0
    user.locked_until = None
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
        user.failed_attempts = int(user.failed_attempts or 0) + 1
        if user.failed_attempts >= 3:
            _lock_user(user, minutes=60)
        db.commit()
        audit_log(db, actor=email, action="OTP_FAIL", entity="users", entity_id=str(user.id))
        raise HTTPException(status_code=401, detail="Invalid OTP")

    # OTP ok
    user.failed_attempts = 0
    user.locked_until = None
    db.commit()

    # single active session
    session_id = set_single_session(db, user.id)

    token = create_access_token({"sub": user.email, "sid": session_id}, expires_minutes=30)
    audit_log(db, actor=email, action="OTP_OK_TOKEN", entity="users", entity_id=str(user.id), meta={"sid": session_id})
    return Token(access_token=token, token_type="bearer")
