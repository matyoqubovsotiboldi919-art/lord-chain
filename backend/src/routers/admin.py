# backend/src/routers/admin.py
from __future__ import annotations

import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user import User
from src.models.audit_log import AuditLog
from src.services.audit import audit_log

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev_admin_token_change_me")


def require_admin(x_admin_token: str | None = Header(default=None)):
    if not x_admin_token or not secrets.compare_digest(x_admin_token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Admin unauthorized")


@router.post("/login")
def admin_login(password: str):
    if not secrets.compare_digest(password, ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid admin password")
    return {"admin_token": ADMIN_TOKEN}


@router.post("/freeze/{email}")
def freeze_user(email: str, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    u = db.query(User).filter(User.email == email.lower().strip()).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.is_frozen = True
    db.commit()
    audit_log(db, actor="ADMIN", action="ADMIN_FREEZE", entity="users", entity_id=str(u.id), meta={"email": u.email})
    return {"detail": "Frozen", "email": u.email}


@router.post("/unfreeze/{email}")
def unfreeze_user(email: str, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    u = db.query(User).filter(User.email == email.lower().strip()).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.is_frozen = False
    db.commit()
    audit_log(db, actor="ADMIN", action="ADMIN_UNFREEZE", entity="users", entity_id=str(u.id), meta={"email": u.email})
    return {"detail": "Unfrozen", "email": u.email}


@router.get("/audit", response_model=list[dict])
def audit_latest(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [
        {
            "actor": r.actor,
            "action": r.action,
            "entity": r.entity,
            "entity_id": r.entity_id,
            "meta": r.meta,
            "created_at": str(r.created_at),
        }
        for r in rows
    ]
