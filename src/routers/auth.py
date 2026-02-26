# backend/src/routers/auth.py
from __future__ import annotations

from datetime import datetime, timedelta
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


def _is_locked(user: User) -> bool:
    # ba'zi modelda locked_until/lock_until bo'lishi mumkin
    until = getattr(user, "locked_until", None)
    if until is None:
        until = getattr(user, "lock_until", None)
    return bool(until and until > datetime.utcnow())


def _set_lock(user: User, minutes: int = 60):
    until = datetime.utcnow() + timedelta(minutes=minutes)
    if hasattr(user, "locked_until"):
        user.locked_until = until
    elif hasattr(user, "lock_until"):
        user.lock_until = until

    if hasattr(user, "failed_attempts"):
        user.failed_attempts = 0
    elif hasattr(user, "failed_login_attempts"):
        user.failed_login_attempts = 0


def _inc_fail(user: User) -> int:
    if hasattr(user, "failed_attempts"):
        user.failed_attempts = int(user.failed_attempts or 0) + 1
        return user.failed_attempts
    if hasattr(user, "failed_login_attempts"):
        user.failed_login_attempts = int(user.failed_login_attempts or 0) + 1
        return user.failed_login_attempts
    return 0


def _reset_fail(user: User):
    if hasattr(user, "failed_attempts"):
        user.failed_attempts = 0
    if hasattr(user, "failed_login_attempts"):
        user.failed_login_attempts = 0
    if hasattr(user, "locked_until"):
        user.locked_until = None
    if hasattr(user, "lock_until"):
        user.lock_until = None


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    email = payload.email.lower().strip()

    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    address = f"LORD_{uuid4().hex}"

    user_kwargs = dict(
        email=email,
        password_hash=hash_password(payload.password),
        address=address,
        balance="1000.00000000",
        is_active=True,
        is_frozen=False,
    )

    # fail/lock ustunlari bo‘lsa to‘ldirib qo‘yamiz
    if hasattr(User, "failed_attempts"):
        user_kwargs["failed_attempts"] = 0
    if hasattr(User, "failed_login_attempts"):
        user_kwargs["failed_login_attempts"] = 0
    if hasattr(User, "locked_until"):
        user_kwargs["locked_until"] = None
    if hasattr(User, "lock_until"):
        user_kwargs["lock_until"] = None

    user = User(**user_kwargs)

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

    if not verify_password(payload.password, user.password_hash):
        fails = _inc_fail(user)
        if fails >= 3:
            _set_lock(user, minutes=60)
        db.commit()
        audit_log(db, actor=email, action="LOGIN_FAIL", entity="users", entity_id=str(user.id))
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # success
    _reset_fail(user)
    db.commit()

    # 1) avval JWT yaratamiz (sid keyin qo‘shamiz)
    token_tmp = create_access_token({"sub": user.email}, expires_minutes=30)

    # 2) sessions jadvali jwt_token NOT NULL bo‘lgani uchun shu tokenni beramiz
    session_id = set_single_session(db, user.id, jwt_token=token_tmp)

    # 3) yakuniy token (sid bilan)
    token = create_access_token({"sub": user.email, "sid": session_id}, expires_minutes=30)

    # xohlasangiz sessiondagi tokenni yangilab qo'yish ham mumkin,
    # lekin hozir shart emas — NOT NULL muammo hal bo‘ldi.

    audit_log(db, actor=email, action="LOGIN_OK_TOKEN", entity="users", entity_id=str(user.id), meta={"sid": session_id})
    return Token(access_token=token, token_type="bearer")