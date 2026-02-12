# backend/src/services/security.py
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

JWT_SECRET = os.environ.get("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = os.environ.get("JWT_ALG", "HS256")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(payload: dict[str, Any], expires_minutes: int = 30) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expires_minutes)
    to_encode = dict(payload)
    to_encode.update({"iat": int(now.timestamp()), "exp": int(exp.timestamp())})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)
