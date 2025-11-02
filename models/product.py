from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Product:
    name: str
    size: str  # S, M, L, XL, XXL
    selling_price: float
    cost_per_piece: float
    pieces_per_pack: int
    id: Optional[int] = None
    
    def calculate_profit(self, quantity: int, discount: float = 0) -> float:
        """Calculate profit for given quantity with optional discount"""
        total_revenue = (self.selling_price * quantity) * (1 - discount)
        total_cost = self.cost_per_piece * quantity
        return total_revenue - total_cost

@dataclass
class RawMaterial:
    name: str
    unit: str  # roll, kg, pack, pcs
    cost_per_unit: float
    id: Optional[int] = None

@dataclass
class ProductionBatch:
    product_id: int
    quantity_produced: int
    materials_used: List[dict]  # [{material_id: 1, quantity: 2}, ...]
    labor_cost: float
    notes: str = ""
    id: Optional[int] = None
