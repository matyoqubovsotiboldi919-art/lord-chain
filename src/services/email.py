import os
import smtplib
from email.message import EmailMessage


def send_otp_email(to_email: str, code: str) -> None:
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    email_from = os.getenv("EMAIL_FROM", smtp_user)

    if not smtp_user or not smtp_pass:
        raise RuntimeError("SMTP_USER/SMTP_PASS is not set")

    # ba'zan Render envda bo'sh joy bilan qo'yib yuboriladi: "abcd efgh ..."
    smtp_pass = smtp_pass.replace(" ", "")

    msg = EmailMessage()
    msg["Subject"] = "LORD Chain OTP"
    msg["From"] = email_from
    msg["To"] = to_email
    msg.set_content(
        f"Your verification code is: {code}\n\n"
        f"This code expires soon. If you didn't request it, ignore this email."
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
