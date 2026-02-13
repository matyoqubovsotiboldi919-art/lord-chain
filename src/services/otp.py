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
    # DB timezone=False -> naive datetime
    return datetime.utcnow()


def _gen_otp6() -> str:
    return f"{random.randint(0, 999999):06d}"


def _send_email(to_email: str, code: str, purpose: str = "LOGIN") -> None:
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    email_from = os.getenv("EMAIL_FROM") or smtp_user

    if not smtp_user or not smtp_pass or not email_from:
        raise RuntimeError("SMTP_USER/SMTP_PASS/EMAIL_FROM env lar to‘liq set qilinmagan")

    # Ba'zida envga bo'sh joy bilan qo'yib yuboriladi
    smtp_pass = smtp_pass.replace(" ", "")

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = to_email
    msg["Subject"] = f"LORD Chain OTP ({purpose})"
    msg.set_content(
        f"Sizning 6 xonali tasdiqlash kodingiz: {code}\n\n"
        f"Kod {OTP_TTL_MINUTES} daqiqa ichida eskiradi."
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)


def issue_otp(db: Session, user: User, purpose: str = "LOGIN") -> OTPCode:
    """
    auth.py aynan shu funksiyani chaqiradi:
      - yangi OTP yaratadi
      - eski aktiv OTPlarni bekor qiladi
      - DB'ga yozadi
      - user.email ga yuboradi
    """
    # eski ishlatilmagan OTPlarni bekor qilamiz (tartib uchun)
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

    _send_email(to_email=user.email, code=code, purpose=purpose)
    return otp


def verify_otp(db: Session, user: User, code: str) -> bool:
    """
    auth.py verify_otp shu funksiyani ishlatadi.
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
