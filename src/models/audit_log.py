from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from src.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    # ✅ AUDIT LOG uchun ID INTEGER bo‘lib qoladi (DBdagi SERIAL bilan mos)
    id = Column(Integer, primary_key=True, index=True)

    # Kim bajardi: "user:<uuid>" / "admin" / "system" kabi
    actor = Column(String(64), nullable=False, default="system")

    # Nima qildi: "REGISTER" / "LOGIN" / "TX_CREATE" / "FREEZE_USER" ...
    action = Column(String(64), nullable=False)

    # Qaysi obyektga tegishli: "user" / "transaction" ...
    entity = Column(String(32), nullable=True)

    # Obyekt ID si (uuid yoki boshqa)
    entity_id = Column(String(64), nullable=True)

    # Qo‘shimcha ma’lumot (JSON)
    meta = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
