from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class StockItem:
    item_type: str  # raw, finished
    item_name: str
    quantity: int
    size: Optional[str] = None
    id: Optional[int] = None
    last_updated: Optional[datetime] = None
