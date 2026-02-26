# backend/src/models/user.py

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base  # agar Base boshqa joyda bo'lsa ayting


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)

  
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    address: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    balance: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=Decimal("0"))

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_frozen: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lock_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    # relationships (Transaction modeli bo'lsa ishlaydi)
    outgoing_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_id",
        back_populates="sender",
    )
    incoming_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_id",
        back_populates="receiver",
    )