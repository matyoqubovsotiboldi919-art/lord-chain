# src/services/security.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

# ----------------------------
# Password hashing (bcrypt)
# ----------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    """Hash plain password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Verify plain password against stored bcrypt hash."""
    return pwd_context.verify(password, password_hash)


# ----------------------------
# JWT helpers
# ----------------------------

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(
    *,
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """
    Create JWT access token.

    - subject: usually user_id (uuid) as string
    - extra_claims: optional additional claims (e.g. {"role": "user"})
    """
    now = _utcnow()
    exp = now + timedelta(minutes=expires_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, secret_key, algorithm=algorithm)

def decode_access_token(
    token: str,
    *,
    secret_key: str,
    algorithm: str,
) -> dict[str, Any]:
    """
    Decode and validate JWT token.
    Raises ValueError if invalid.
    """
    try:
        data = jwt.decode(token, secret_key, algorithms=[algorithm])
        return data
    except JWTError as e:
        raise ValueError("Invalid token") from e