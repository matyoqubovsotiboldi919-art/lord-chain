# src/services/otp.py
from __future__ import annotations

import os
import random
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from sqlalchemy.orm import Session

from src.models.otp import OTPCode

from src.models.user import User


OTP_TTL_MINUTES = int(os.getenv("OTP_TTL_MINUTES", "10"))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "3"))


def _now_utc_naive() -> datetime:
    # DB'da timezone=False ishlatyapsiz, shuning uchun naive datetime qaytaramiz
    return datetime.utcnow()


def _gen_otp6() -> str:
    return f"{random.randint(0, 999999):06d}"


def _send_email(to_email: str, subject: str, body: str) -> None:
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    email_from = os.getenv("EMAIL_FROM") or smtp_user

    if not smtp_user or not smtp_pass or not email_from:
        raise RuntimeError("SMTP_USER/SMTP_PASS/EMAIL_FROM env lar to‘liq set qilinmagan")

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Gmail SMTP: STARTTLS (587)
    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)


def create_and_send_login_otp(db: Session, user: User) -> OTPCode:
    """
    Login tasdiqlash uchun: user.email ga OTP yuboradi va DB'ga yozadi.
    """
    return _create_and_send_otp(db=db, user=user, purpose="LOGIN")


def create_and_send_tx_otp(db: Session, user: User) -> OTPCode:
    """
    Transaction tasdiqlash uchun: user.email ga OTP yuboradi va DB'ga yozadi.
    """
    return _create_and_send_otp(db=db, user=user, purpose="TX")


def _create_and_send_otp(db: Session, user: User, purpose: str) -> OTPCode:
    # eski ishlatilmagan OTPlarni bekor qilish (ixtiyoriy, lekin tartibli)
    db.query(OTPCode).filter(
        OTPCode.user_id == user.id,
        OTPCode.is_used == False,  # noqa: E712
    ).update({"is_used": True})
    db.commit()

    code = _gen_otp6()
    expires_at = _now_utc_naive() + timedelta(minutes=OTP_TTL_MINUTES)

    otp = OTPCode(
        user_id=user.id,
        code=code,
        expires_at=expires_at,
        attempts=0,
        is_used=False,
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)

    subject = f"LORD Chain OTP ({purpose})"
    body = (
        f"Sizning tasdiqlash kodingiz: {code}\n\n"
        f"Kod {OTP_TTL_MINUTES} daqiqa ichida eskiradi.\n"
        f"Agar bu siz bo‘lmasangiz, hisobingiz xavfsizligi uchun parolingizni almashtiring."
    )

    _send_email(to_email=user.email, subject=subject, body=body)
    return otp


def verify_otp(db: Session, user: User, code: str) -> bool:
    """
    Berilgan code to‘g‘riligini tekshiradi.
    - muddati o‘tmagan bo‘lishi kerak
    - ishlatilmagan bo‘lishi kerak
    - urinishlar limiti oshmagan bo‘lishi kerak
    To‘g‘ri bo‘lsa: is_used=True qilib qo‘yadi va True qaytaradi.
    """
    code = (code or "").strip()
    if len(code) != 6 or not code.isdigit():
        return False

    otp = (
        db.query(OTPCode)
        .filter(
            OTPCode.user_id == user.id,
            OTPCode.is_used == False,  # noqa: E712
        )
        .order_by(OTPCode.created_at.desc())
        .first()
    )

    if not otp:
        return False

    now = _now_utc_naive()
    if otp.expires_at <= now:
        otp.is_used = True
        db.commit()
        return False

    if otp.attempts >= OTP_MAX_ATTEMPTS:
        otp.is_used = True
        db.commit()
        return False

    if otp.code != code:
        otp.attempts = otp.attempts + 1
        db.commit()
        return False

    otp.is_used = True
    db.commit()
    return True
