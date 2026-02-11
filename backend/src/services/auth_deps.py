from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.session import get_db
from src.models.user import User
from src.services.security import decode_access_token
from src.services.runtime_state import ACTIVE_SESSIONS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(token, settings.SECRET_KEY)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("sub")
    sid = payload.get("sid")
    if not email or not sid:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Single active session tekshiruvi
    active_sid = ACTIVE_SESSIONS.get(email)
    if active_sid is None or active_sid != sid:
        raise HTTPException(status_code=401, detail="Session expired (logged in elsewhere)")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if user.is_frozen:
        raise HTTPException(status_code=403, detail="Account is frozen")

    return user
