import time
from fastapi import Header, HTTPException

from src.services.admin_runtime import ADMIN_SESSIONS, ADMIN_SESSION_TIMEOUT_SECONDS


def require_admin(x_admin_token: str | None = Header(default=None)) -> str:
    """
    Admin endpointlar uchun session token tekshiradi.
    30 min timeout: har requestda token expiry yangilanadi.
    """
    if not x_admin_token:
        raise HTTPException(status_code=401, detail="Admin token required")

    sess = ADMIN_SESSIONS.get(x_admin_token)
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    now = int(time.time())
    if now > int(sess["exp"]):
        ADMIN_SESSIONS.pop(x_admin_token, None)
        raise HTTPException(status_code=401, detail="Admin session expired")

    # sliding timeout: aktiv bo‘lsa, yana 30 minutga uzayadi
    sess["last"] = now
    sess["exp"] = now + ADMIN_SESSION_TIMEOUT_SECONDS
    return x_admin_token
