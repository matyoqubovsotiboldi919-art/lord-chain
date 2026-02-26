# backend/src/services/audit.py
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from src.models.audit_log import AuditLog


def audit_log(
    db: Session,
    actor: str,
    action: str,
    entity: str,
    entity_id: str,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    try:
        rec = AuditLog(
            actor=actor,
            action=action,
            entity=entity,
            entity_id=entity_id,
            meta=meta,
        )
        db.add(rec)
        db.commit()
    except Exception:
        # Audit DB sxemasi mos kelmasa ham asosiy funksiyalar yiqilmasin
        db.rollback()
        return