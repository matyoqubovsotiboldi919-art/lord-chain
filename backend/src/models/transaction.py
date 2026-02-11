# backend/src/models/transaction.py
from __future__ import annotations

from uuid import uuid4
from datetime import datetime

from sqlalchemy import String, DateTime, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    from_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    to_address: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)

    # 1 tx = 1 block
    block_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    prev_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    block_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)

    # optional: user link (kim yubordi)
    user_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default="now()")
