import os

class Settings:
    PROJECT_NAME = "LORD Chain"
    API_V1_PREFIX = "/api/v1"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/lord_chain"
    )

    SECRET_KEY = os.getenv("SECRET_KEY", "change_me_secret")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    OTP_EXPIRE_SECONDS = int(os.getenv("OTP_EXPIRE_SECONDS", "300"))
    OTP_MAX_TRIES = int(os.getenv("OTP_MAX_TRIES", "3"))
    LOCK_MINUTES = int(os.getenv("LOCK_MINUTES", "60"))

    SYSTEM_MINT_AMOUNT = os.getenv("SYSTEM_MINT_AMOUNT", "1000.00000000")

    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "0") == "1"

    # SMTP (6.5)
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@lord.local")
    SMTP_TLS = os.getenv("SMTP_TLS", "1") == "1"

settings = Settings()
