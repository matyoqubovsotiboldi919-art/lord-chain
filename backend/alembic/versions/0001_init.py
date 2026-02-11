"""init

Revision ID: 0001_init
Revises: 
Create Date: 2026-02-10
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=128), nullable=False),
        sa.Column("balance", sa.Numeric(20, 8), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("is_frozen", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("failed_attempts", sa.Integer(), server_default="0"),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_address", "users", ["address"], unique=True)

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_address", sa.String(length=128), nullable=False),
        sa.Column("to_address", sa.String(length=128), nullable=False),
        sa.Column("amount", sa.Numeric(20, 8), nullable=False),
        sa.Column("block_index", sa.Integer(), nullable=False),
        sa.Column("prev_hash", sa.String(length=128), nullable=False),
        sa.Column("block_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_transactions_from_address", "transactions", ["from_address"])
    op.create_index("ix_transactions_to_address", "transactions", ["to_address"])
    op.create_index("ix_transactions_block_index", "transactions", ["block_index"])
    op.create_index("ix_transactions_block_hash", "transactions", ["block_hash"], unique=True)
    op.create_index("ix_transactions_from_to", "transactions", ["from_address", "to_address"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_email", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("detail", sa.String(length=1000), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_logs_actor_email", "audit_logs", ["actor_email"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])

def downgrade():
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_email", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_transactions_from_to", table_name="transactions")
    op.drop_index("ix_transactions_block_hash", table_name="transactions")
    op.drop_index("ix_transactions_block_index", table_name="transactions")
    op.drop_index("ix_transactions_to_address", table_name="transactions")
    op.drop_index("ix_transactions_from_address", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_users_address", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
