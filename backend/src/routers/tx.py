# backend/src/routers/tx.py
from __future__ import annotations

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.db.session import get_db
from src.deps.auth import get_current_user
from src.models.user import User
from src.models.transaction import Transaction

from src.schemas.transaction import TxCreate, TxOut
from src.services.blockchain import build_block
from src.services.audit import audit_log

router = APIRouter(prefix="/api/v1/tx", tags=["transactions"])


@router.post("/create", response_model=TxOut)
def create_tx(payload: TxCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.is_frozen:
        raise HTTPException(status_code=403, detail="Account is frozen")

    amount = Decimal(str(payload.amount)).quantize(Decimal("0.00000001"))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    to_addr = payload.to_address.strip()
    if len(to_addr) < 3:
        raise HTTPException(status_code=400, detail="Invalid to_address")

    # atomic transaction
    try:
        with db.begin():
            # lock sender row
            sender = db.query(User).filter(User.id == user.id).with_for_update().one()

            if Decimal(str(sender.balance)) < amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")

            # find receiver by address
            receiver = db.query(User).filter(User.address == to_addr).with_for_update().first()
            if not receiver:
                raise HTTPException(status_code=404, detail="Receiver not found")

            # build block hashes
            block_index, prev_hash, block_hash = build_block(db, sender.address, receiver.address, str(amount))

            # update balances
            sender.balance = (Decimal(str(sender.balance)) - amount)
            receiver.balance = (Decimal(str(receiver.balance)) + amount)

            tx = Transaction(
                from_address=sender.address,
                to_address=receiver.address,
                amount=str(amount),
                block_index=block_index,
                prev_hash=prev_hash,
                block_hash=block_hash,
                user_id=sender.id,
            )
            db.add(tx)

        audit_log(db, actor=user.email, action="TX_CREATE", entity="transactions", entity_id=str(tx.id), meta={
            "from": tx.from_address, "to": tx.to_address, "amount": str(amount), "block_index": block_index
        })
        db.refresh(tx)
        return tx

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TX failed: {type(e).__name__}")


@router.get("/history", response_model=list[TxOut])
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # oxirgi 50 tx (soddaroq)
    rows = (
        db.query(Transaction)
        .filter(Transaction.from_address == user.address)
        .order_by(Transaction.block_index.desc())
        .limit(50)
        .all()
    )
    return rows
