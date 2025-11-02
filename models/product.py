from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    name: str
    size: str  # S, M, L, XL, XXL
    selling_price: float
    cost_per_piece: float
    pieces_per_pack: int
    id: Optional[int] = None
    
    def calculate_profit(self, quantity: int) -> float:
        """Calculate profit for given quantity"""
        return (self.selling_price - self.cost_per_piece) * quantity
