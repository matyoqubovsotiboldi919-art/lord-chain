# backend/src/core/config.py
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

    LOCK_MINUTES = int(os.getenv("LOCK_MINUTES", "60"))

    SYSTEM_MINT_AMOUNT = os.getenv("SYSTEM_MINT_AMOUNT", "1000.00000000")

    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "0") == "1"


settings = Settings()