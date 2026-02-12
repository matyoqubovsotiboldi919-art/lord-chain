# backend/src/services/blockchain.py
from __future__ import annotations

import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.models.transaction import Transaction


SYSTEM_MINT = "SYSTEM_MINT"


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def get_last_block(db: Session) -> tuple[int, str]:
    # (last_index, last_hash)
    row = db.execute(text("select block_index, block_hash from transactions order by block_index desc limit 1")).fetchone()
    if not row:
        return (0, "GENESIS")
    return (int(row[0]), str(row[1]))


def build_block(db: Session, from_addr: str, to_addr: str, amount: str) -> tuple[int, str, str]:
    last_index, last_hash = get_last_block(db)
    new_index = last_index + 1
    payload = f"{new_index}|{last_hash}|{from_addr}|{to_addr}|{amount}"
    new_hash = _sha256(payload)
    return new_index, last_hash, new_hash



import hashlib
import json

def calculate_hash(block: dict) -> str:
    """
    Block dict dan deterministic hash chiqaradi.
    chain_verify.py shu funksiyani kutyapti.
    """
    payload = json.dumps(block, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
