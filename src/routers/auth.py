# backend/src/routers/auth.py
from __future__ import annotations

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

LOCK_MINUTES = 60
MAX_FAILS = 3


def _now_utc_naive() -> datetime:
    return datetime.utcnow()


def _get_lock_until(user: User):
    if hasattr(user, "locked_until"):
        return getattr(user, "locked_until")
    if hasattr(user, "lock_until"):
        return getattr(user, "lock_until")
    return None


def _set_lock_until(user: User, value):
    if hasattr(user, "locked_until"):
        setattr(user, "locked_until", value)
    if hasattr(user, "lock_until"):
        setattr(user, "lock_until", value)


def _get_fails(user: User) -> int:
    if hasattr(user, "failed_attempts"):
        return int(getattr(user, "failed_attempts") or 0)
    if hasattr(user, "failed_login_attempts"):
        return int(getattr(user, "failed_login_attempts") or 0)
    return 0


def _set_fails(user: User, value: int):
    if hasattr(user, "failed_attempts"):
        setattr(user, "failed_attempts", int(value))
    if hasattr(user, "failed_login_attempts"):
        setattr(user, "failed_login_attempts", int(value))


def _is_locked(user: User) -> bool:
    until = _get_lock_until(user)
    if not until:
        return False
    try:
        now = _now_utc_naive()
        if getattr(until, "tzinfo", None) is not None:
            now = datetime.now(timezone.utc)
        return until > now
    except Exception:
        return False


def _lock_user(user: User, minutes: int = LOCK_MINUTES):
    _set_lock_until(user, _now_utc_naive() + timedelta(minutes=minutes))
    _set_fails(user, 0)


def _reset_lock_and_fails(user: User):
    _set_fails(user, 0)
    _set_lock_until(user, None)


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    email = payload.email.lower().strip()

    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    address = f"LORD_{uuid4().hex}"

    user_kwargs = {
        "email": email,
        "password_hash": hash_password(payload.password),
        "address": address,
        "balance": "1000.00000000",
        "is_active": True,
        "is_frozen": False,
    }

    user = User(**user_kwargs)
    _reset_lock_and_fails(user)

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

    if getattr(user, "is_frozen", False):
        raise HTTPException(status_code=403, detail="Account is frozen")

    if _is_locked(user):
        raise HTTPException(status_code=403, detail="Account is locked. Try later.")

    if not hasattr(user, "password_hash") or not user.password_hash:
        raise HTTPException(status_code=500, detail="User password not set")

    if not verify_password(payload.password, user.password_hash):
        fails = _get_fails(user) + 1
        _set_fails(user, fails)
        if fails >= MAX_FAILS:
            _lock_user(user, minutes=LOCK_MINUTES)
        db.commit()
        audit_log(db, actor=email, action="LOGIN_FAIL", entity="users", entity_id=str(user.id))
        raise HTTPException(status_code=401, detail="Invalid credentials")

    _reset_lock_and_fails(user)
    db.commit()

    # sessions.jwt_token NOT NULL -> avval token
    token_tmp = create_access_token({"sub": user.email}, expires_minutes=30)

    # single session yozish (jwt_token bilan)
    session_id = set_single_session(db, user.id, jwt_token=token_tmp)

    # final token sid bilan
    token = create_access_token({"sub": user.email, "sid": str(session_id)}, expires_minutes=30)

    audit_log(db, actor=email, action="LOGIN_OK_TOKEN", entity="users", entity_id=str(user.id), meta={"sid": str(session_id)})
    return Token(access_token=token, token_type="bearer")