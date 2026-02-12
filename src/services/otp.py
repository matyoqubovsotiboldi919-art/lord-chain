# backend/src/services/otp.py
from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.models.otp import OTPCode


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def issue_otp(db: Session, user_id) -> OTPCode:
    code = generate_otp()
    expires = datetime.utcnow() + timedelta(minutes=5)

    # eski ishlatilmagan OTP’larni “used” qilib qo‘yamiz
    db.query(OTPCode).filter(OTPCode.user_id == user_id, OTPCode.is_used == False).update({"is_used": True})
    db.commit()

    rec = OTPCode(user_id=user_id, code=code, expires_at=expires, attempts=0, is_used=False)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def verify_otp(db: Session, user_id, otp: str) -> bool:
    rec = (
        db.query(OTPCode)
        .filter(OTPCode.user_id == user_id, OTPCode.is_used == False)
        .order_by(OTPCode.created_at.desc())
        .first()
    )
    if not rec:
        return False

    if datetime.utcnow() > rec.expires_at:
        rec.is_used = True
        db.commit()
        return False

    rec.attempts = int(rec.attempts or 0) + 1
    if rec.attempts > 5:
        rec.is_used = True
        db.commit()
        return False

    if secrets.compare_digest(rec.code, str(otp)):
        rec.is_used = True
        db.commit()
        return True

    db.commit()
    return False
