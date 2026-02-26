"""add password_hash to users

Revision ID: 938ec1ed5a4e
Revises: f8de1919bf07
Create Date: 2026-02-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql  # ✅ MUHIM: postgresql.TIMESTAMP uchun kerak


# revision identifiers, used by Alembic.
revision: str = "938ec1ed5a4e"
down_revision: Union[str, None] = "f8de1919bf07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Yangi ustunlar
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=False))
    op.add_column("users", sa.Column("address", sa.String(length=64), nullable=False))
    op.add_column("users", sa.Column("balance", sa.Numeric(precision=20, scale=8), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("lock_until", sa.DateTime(timezone=True), nullable=True))

    # 2) email: 255 -> 320
    op.alter_column(
        "users",
        "email",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.String(length=320),
        existing_nullable=False,
    )

    # 3) created_at: timezone yoqish
    op.alter_column(
        "users",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )

    # 4) index
    op.create_index("ix_users_address", "users", ["address"], unique=False)

    # 5) Eski hashed_password bo‘lsa olib tashlash
    op.drop_column("users", "hashed_password")

    # server_default larni tozalash (DB’da doimiy default kerak bo‘lmasa)
    op.alter_column("users", "balance", server_default=None)
    op.alter_column("users", "failed_login_attempts", server_default=None)


def downgrade() -> None:
    # downgrade: orqaga qaytarish
    op.add_column("users", sa.Column("hashed_password", sa.VARCHAR(length=255), nullable=False))
    op.drop_index("ix_users_address", table_name="users")

    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )

    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=320),
        type_=sa.VARCHAR(length=255),
        existing_nullable=False,
    )

    op.drop_column("users", "lock_until")
    op.drop_column("users", "failed_login_attempts")
    op.drop_column("users", "balance")
    op.drop_column("users", "address")
    op.drop_column("users", "password_hash")