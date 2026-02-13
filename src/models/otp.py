# src/models/otp.py
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from src.db.base import Base


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=False), nullable=False)

    attempts = Column(Integer, server_default="0", nullable=False)
    is_used = Column(Boolean, server_default="false", nullable=False)

    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
