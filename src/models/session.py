from sqlalchemy.orm import Session
from sqlalchemy import update
from uuid import UUID

from src.models.session import UserSession


def set_single_session(db: Session, user_id: UUID, jwt_token: str):
    """
    Foydalanuvchi uchun faqat bitta aktiv session qoldiradi.
    Oldingi sessionlarni inactive qiladi.
    """

    # 1. Barcha eski sessionlarni inactive qilamiz
    db.execute(
        update(UserSession)
        .where(UserSession.user_id == user_id)
        .values(is_active=False)
    )

    # 2. Yangi session yaratamiz
    new_session = UserSession(
        user_id=user_id,
        jwt_token=jwt_token,
        is_active=True
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session
