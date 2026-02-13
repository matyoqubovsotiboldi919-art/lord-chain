import uuid
from sqlalchemy.orm import Session

from src.models.session import UserSession
from src.models.user import User


def set_single_session(db: Session, user: User, jwt_token: str) -> UserSession:
    # eski sessionlarni inactive qilamiz
    db.query(UserSession).filter(UserSession.user_id == user.id).update(
        {"is_active": False}
    )

    # yangi session yaratamiz
    new_session = UserSession(
        id=uuid.uuid4(),
        user_id=user.id,
        jwt_token=jwt_token,
        is_active=True,
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session
