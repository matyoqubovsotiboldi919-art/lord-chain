# backend/src/services/sessions.py
from __future__ import annotations

import secrets
from sqlalchemy.orm import Session

from backend.src.models.session import UserSession


def new_session_id() -> str:
    return secrets.token_hex(16)


def set_single_session(db: Session, user_id):
    # old sessions delete
    db.query(UserSession).filter(UserSession.user_id == user_id).delete()
    sid = new_session_id()
    rec = UserSession(user_id=user_id, session_id=sid)
    db.add(rec)
    db.commit()
    return sid


def get_session(db: Session, user_id):
    return db.query(UserSession).filter(UserSession.user_id == user_id).first()
