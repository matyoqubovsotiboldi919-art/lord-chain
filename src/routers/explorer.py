from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.session import get_db
from src.models.transaction import Transaction
from src.services.chain_verify import verify_chain

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/explorer", tags=["explorer"])


@router.get("/tx/{block_hash}")
def get_tx(block_hash: str, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.block_hash == block_hash).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "block_index": tx.block_index,
        "block_hash": tx.block_hash,
        "prev_hash": tx.prev_hash,
        "from_address": tx.from_address,
        "to_address": tx.to_address,
        "amount": str(tx.amount),
        "created_at": str(tx.created_at),
    }


@router.get("/address/{address}")
def list_by_address(address: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Transaction)
        .filter((Transaction.from_address == address) | (Transaction.to_address == address))
        .order_by(Transaction.block_index.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "block_index": r.block_index,
            "block_hash": r.block_hash,
            "prev_hash": r.prev_hash,
            "from_address": r.from_address,
            "to_address": r.to_address,
            "amount": str(r.amount),
            "created_at": str(r.created_at),
        }
        for r in rows
    ]


@router.get("/verify-chain")
def verify(db: Session = Depends(get_db)):
    return verify_chain(db)
