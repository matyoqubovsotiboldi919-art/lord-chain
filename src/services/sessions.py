# backend/src/services/sessions.py
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from uuid import uuid4
from typing import Optional

from sqlalchemy.orm import Session

from src.models.session import UserSession


def utcnow():
    return datetime.now(timezone.utc)


def set_single_session(db: Session, user_id, jwt_token: Optional[str] = None) -> str:
    """
    1 user = 1 active session.
    Eski sessionlar delete qilinmaydi (delete yo'q), faqat revoke qilinadi.
    jwt_token param: eski kodlar bilan moslashish uchun OPTIONAL.
    """
    # 1) Oldingi active sessionlarni revoke qilamiz
    db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True,  # noqa: E712
    ).update(
        {"is_active": False, "revoked_at": utcnow()},
        synchronize_session=False,
    )

    # 2) Yangi session
    sid = uuid4().hex

    # Ba'zi eski modelda token saqlash ustuni bo'lishi mumkin.
    # Shuning uchun faqat attribute bor bo'lsa set qilamiz.
    rec = UserSession(
        user_id=user_id,
        session_id=sid,
        is_active=True,
        created_at=utcnow(),
        expires_at=utcnow() + timedelta(minutes=60),
        revoked_at=None,
    )

    # Optional: agar modelda jwt_token ustuni bo'lsa
    if jwt_token is not None and hasattr(rec, "jwt_token"):
        setattr(rec, "jwt_token", jwt_token)

    db.add(rec)
    db.commit()
    return sid