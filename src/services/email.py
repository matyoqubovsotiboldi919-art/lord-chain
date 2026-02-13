import os
import smtplib
from email.message import EmailMessage

def send_otp_email(to_email: str, code: str, purpose: str):
    msg = EmailMessage()
    msg["Subject"] = f"LORD OTP ({purpose})"
    msg["From"] = os.getenv("EMAIL_FROM")
    msg["To"] = to_email
    msg.set_content(f"Your verification code is: {code}")

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        server.send_message(msg)
