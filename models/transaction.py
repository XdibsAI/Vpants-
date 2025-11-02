from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Transaction:
    type: str  # sale, purchase, expense, withdrawal, se_income
    category: str
    amount: float
    quantity: Optional[int] = None
    size: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
