# backend/src/services/audit.py
from __future__ import annotations

from sqlalchemy.orm import Session
from src.models.audit_log import AuditLog


def audit_log(db: Session, actor: str, action: str, entity: str, entity_id: str = "", meta: dict | None = None):
    rec = AuditLog(
        actor=actor,
        action=action,
        entity=entity,
        entity_id=entity_id or "",
        meta=meta or {},
    )
    db.add(rec)
    db.commit()
