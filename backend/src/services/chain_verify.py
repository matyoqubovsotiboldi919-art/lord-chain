from decimal import Decimal, ROUND_DOWN
from sqlalchemy.orm import Session

from src.models.transaction import Transaction
from src.services.blockchain import calculate_hash

AMOUNT_Q = Decimal("0.00000001")

def _norm_amount(amount: Decimal) -> str:
    a = Decimal(amount).quantize(AMOUNT_Q, rounding=ROUND_DOWN)
    return format(a, "f")

def verify_chain(db: Session) -> dict:
    """
    Zanjirni 1..N bo‘yicha tekshiradi:
    - prev_hash mosligi
    - block_hash qayta hisoblanganda mosligi
    """
    rows = db.query(Transaction).order_by(Transaction.block_index.asc()).all()
    if not rows:
        return {"ok": True, "blocks": 0, "detail": "empty"}

    errors = []
    prev = "GENESIS"

    for r in rows:
        amt = _norm_amount(Decimal(r.amount))
        raw = f"{r.block_index}{r.from_address}{r.to_address}{amt}{r.prev_hash}"
        expected_hash = calculate_hash(raw)

        if r.prev_hash != prev:
            errors.append({"block_index": r.block_index, "type": "prev_hash_mismatch", "expected": prev, "got": r.prev_hash})

        if r.block_hash != expected_hash:
            errors.append({"block_index": r.block_index, "type": "block_hash_mismatch"})

        prev = r.block_hash

    return {"ok": len(errors) == 0, "blocks": len(rows), "errors": errors[:50]}
