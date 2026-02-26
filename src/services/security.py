# backend/src/services/security.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(payload: Dict[str, Any], expires_minutes: int | None = None) -> str:
    """
    Always call like:
        create_access_token({"sub": email, "sid": "..."} , expires_minutes=30)
    """
    if expires_minutes is None:
        expires_minutes = int(getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    to_encode = dict(payload)
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(expires_minutes))
    to_encode.update({"exp": expire})

    secret = getattr(settings, "SECRET_KEY", "change_me_secret")
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    secret = getattr(settings, "SECRET_KEY", "change_me_secret")
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid token") from e