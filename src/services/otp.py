# src/services/otp.py
from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.models.otp import OTPCode
from src.models.user import User
from src.services.email import send_otp_email


OTP_TTL_MINUTES = int(os.getenv("OTP_TTL_MINUTES", "10"))          # 10 minut
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "3"))        # 3 ta xato urinish


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _gen_6_digit_code() -> str:
    # 000000..999999
    return f"{secrets.randbelow(1_000_000):06d}"


def create_and_send_otp(db: Session, user: User) -> OTPCode:
    """
    1) Yangi 6 xonali OTP yaratadi
    2) DB ga saqlaydi
    3) user.email ga yuboradi (Gmail SMTP orqali)
    """
    # avvalgi ishlatilmagan OTPlarni xohlasang bekor qilish mumkin (majburiy emas)
    # db.query(OTPCode).filter(
    #     OTPCode.user_id == user.id,
    #     OTPCode.is_used.is_(False),
    #     OTPCode.expires_at > _now_utc().replace(tzinfo=None),
    # ).update({"is_used": True})

    code = _gen_6_digit_code()
    expires_at = _now_utc() + timedelta(minutes=OTP_TTL_MINUTES)

    otp = OTPCode(
        user_id=user.id,
        code=code,
        expires_at=expires_at.replace(tzinfo=None),  # DB TIMESTAMP timezone-siz bo‘lsa
        attempts=0,
        is_used=False,
    )

    db.add(otp)
    db.commit()
    db.refresh(otp)

    # Email yuborish
    send_otp_email(user.email, code)

    return otp


def verify_otp(db: Session, user: User, code: str) -> bool:
    """
    Foydalanuvchining eng oxirgi (latest) ishlatilmagan OTP sini tekshiradi.
    To‘g‘ri bo‘lsa: is_used=True qilib qo‘yadi va True qaytaradi.
    Noto‘g‘ri bo‘lsa: attempts++ qiladi, limitdan oshsa is_used=True qiladi va False qaytaradi.
    """
    code = (code or "").strip()

    otp: OTPCode | None = (
        db.query(OTPCode)
        .filter(OTPCode.user_id == user.id)
        .order_by(desc(OTPCode.created_at))
        .first()
    )

    if not otp:
        return False

    # allaqachon ishlatilgan bo‘lsa
    if otp.is_used:
        return False

    # muddati tugagan bo‘lsa
    now_naive = _now_utc().replace(tzinfo=None)
    if otp.expires_at <= now_naive:
        otp.is_used = True
        db.commit()
        return False

    # urinishlar limiti
    if otp.attempts >= OTP_MAX_ATTEMPTS:
        otp.is_used = True
        db.commit()
        return False

    # kod tekshirish
    if otp.code != code:
        otp.attempts = (otp.attempts or 0) + 1
        if otp.attempts >= OTP_MAX_ATTEMPTS:
            otp.is_used = True
        db.commit()
        return False

    # to‘g‘ri bo‘lsa
    otp.is_used = True
    db.commit()
    return True
