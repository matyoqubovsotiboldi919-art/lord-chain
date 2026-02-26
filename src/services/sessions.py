# backend/src/services/sessions.py
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import uuid4

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from src.models.session import UserSession


def utcnow():
    return datetime.now(timezone.utc)


def _model_columns(model) -> set[str]:
    # SQLAlchemy modelida mavjud column/attr nomlarini olamiz
    return {attr.key for attr in inspect(model).mapper.column_attrs}


def set_single_session(db: Session, user_id, jwt_token: Optional[str] = None) -> str:
    """
    1 user = 1 active session.
    Old sessionlar delete qilinmaydi (delete yo‘q), faqat mavjud columnlar bo‘lsa deactivate qilinadi.
    jwt_token optional (eski kod bilan mos).
    """
    cols = _model_columns(UserSession)

    # 1) Old active sessionlarni deactivate/revoke qilish (faqat mavjud columnlar bo‘lsa)
    update_data = {}

    # ko‘p loyihalarda shu nomlar bo‘ladi:
    if "is_active" in cols:
        update_data["is_active"] = False

    # revoked_at bo‘lmasligi mumkin — shuning uchun tekshiramiz
    if "revoked_at" in cols:
        update_data["revoked_at"] = utcnow()

    # ba’zan "ended_at" bo‘ladi
    if "ended_at" in cols:
        update_data["ended_at"] = utcnow()

    # faqat update_data bo‘lsa update qilamiz
    if update_data and ("user_id" in cols) and ("is_active" in cols):
        db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True,  # noqa: E712
        ).update(update_data, synchronize_session=False)

    # 2) Yangi session yaratish (faqat mavjud columnlar bilan)
    sid = uuid4().hex

    create_data = {}

    if "user_id" in cols:
        create_data["user_id"] = user_id

    # session id column nomi turlicha bo‘lishi mumkin:
    if "session_id" in cols:
        create_data["session_id"] = sid
    elif "sid" in cols:
        create_data["sid"] = sid

    if "is_active" in cols:
        create_data["is_active"] = True

    if "created_at" in cols:
        create_data["created_at"] = utcnow()

    if "expires_at" in cols:
        create_data["expires_at"] = utcnow() + timedelta(minutes=60)

    # token ustuni bo‘lsa qo‘yamiz
    if jwt_token is not None:
        if "jwt_token" in cols:
            create_data["jwt_token"] = jwt_token
        elif "token" in cols:
            create_data["token"] = jwt_token

    rec = UserSession(**create_data)
    db.add(rec)
    db.commit()

    return sid