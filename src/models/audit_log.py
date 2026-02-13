# src/models/audit_log.py
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from src.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    action = Column(String(255), nullable=False)
    ip_address = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
