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
    # DB ko'pincha naive UTC saqlaydi (datetime.utcnow()) — shunga mos qilamiz
    return datetime.utcnow()


def _get_lock_until(user: User):
    # projectda 2 xil nom uchragan: locked_until yoki lock_until
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
    # projectda 2 xil nom uchragan: failed_attempts yoki failed_login_attempts
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
    # until timezone-aware bo'lib qolsa ham xato bermasin:
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

    # Modelda qaysi ustunlar borligini tekshirib, faqat borlarini uzatamiz.
    user_kwargs = {
        "email": email,
        "password_hash": hash_password(payload.password),
        "address": address,
        "balance": "1000.00000000",
        "is_active": True,
        "is_frozen": False,
    }

    # agar modelda fail/lock maydonlari bo'lsa
    if hasattr(User, "failed_attempts") or hasattr(User, "failed_login_attempts"):
        # ikkalasini ham set qiladigan helper ishlatamiz
        # (agar bittasi yo'q bo'lsa helper o'zi skip qiladi)
        pass
    if hasattr(User, "locked_until") or hasattr(User, "lock_until"):
        pass

    user = User(**user_kwargs)
    _reset_lock_and_fails(user)

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

    # password_hash bo'lishi shart
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

    # success
    _reset_lock_and_fails(user)
    db.commit()

    # 1) avval token yaratamiz (sessions jadvali jwt_token NOT NULL bo'lgani uchun)
    token_tmp = create_access_token(data={"sub": user.email}, expires_minutes=30)

    # 2) single session yozamiz (jwt_token bilan)
    session_id = set_single_session(db, user.id, jwt_token=token_tmp)

    # 3) final token (sid bilan)
    token = create_access_token(
        data={"sub": user.email, "sid": str(session_id)},
        expires_minutes=30,
    )

    audit_log(
        db,
        actor=email,
        action="LOGIN_OK_TOKEN",
        entity="users",
        entity_id=str(user.id),
        meta={"sid": str(session_id)},
    )
    return Token(access_token=token, token_type="bearer")