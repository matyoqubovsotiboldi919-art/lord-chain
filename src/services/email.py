# backend/src/services/email.py
from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def send_otp_email(to_email: str, otp: str):
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    from_email = os.environ.get("SMTP_FROM", user or "no-reply@example.com")

    # SMTP sozlanmagan bo‘lsa: DEV rejim
    if not host or not user or not password:
        print(f"[DEV EMAIL OTP] to={to_email} otp={otp}")
        return

    msg = EmailMessage()
    msg["Subject"] = "Your LORD OTP Code"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(f"Your OTP code is: {otp}\nIt expires in 5 minutes.")

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
