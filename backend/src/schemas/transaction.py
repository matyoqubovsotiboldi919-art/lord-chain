# backend/src/schemas/transaction.py
from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field

class TxCreate(BaseModel):
    to_address: str = Field(min_length=3, max_length=128)
    amount: float = Field(gt=0)

class TxOut(BaseModel):
    id: UUID
    from_address: str
    to_address: str
    amount: float
    block_index: int
    prev_hash: str
    block_hash: str

    class Config:
        from_attributes = True
