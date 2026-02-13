# src/models/transaction.py
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID

from src.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    amount = Column(Numeric(20, 8), nullable=False)
    tx_type = Column(String(20), nullable=False)  # deposit/withdraw/transfer

    block_index = Column(String(100), nullable=True)
    prev_hash = Column(String(255), nullable=True)
    block_hash = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
