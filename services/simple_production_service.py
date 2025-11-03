"""
Simplified production service for VPants
"""
import sqlite3
from datetime import datetime
from config.database import get_connection

class SimpleProductionService:
    def __init__(self):
        self.conn = get_connection()
    
    def record_production(self, product_name: str, size: str, quantity: int, cost_per_piece: float):
        """Record simple production - hanya quantity dan cost"""
        cursor = self.conn.cursor()
        
        try:
            total_cost = cost_per_piece * quantity
            
            # Insert production record
            cursor.execute('''
                INSERT INTO production_batches 
                (product_name, size, quantity_produced, labor_cost, materials_cost, total_cost, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_name, size, quantity, total_cost, 0, total_cost, "Produksi sederhana"))
            
            # Update finished goods stock
            cursor.execute('''
                INSERT OR REPLACE INTO stock (item_type, item_name, size, quantity)
                VALUES ('finished', ?, ?, COALESCE(
                    (SELECT quantity FROM stock WHERE item_type='finished' AND item_name=? AND size=?), 0
                ) + ?)
            ''', (product_name, size, product_name, size, quantity))
            
            # Record as expense
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, quantity, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', ('expense', 'production', total_cost, quantity, f"Produksi {quantity}pcs {product_name} {size}"))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_raw_materials_simple(self):
        """Get simplified raw materials list"""
        return [
            (1, "Kain Siap Jahit", "pcs", 25000),
            (2, "Karet Elastis", "meter", 5000),
            (3, "Benang", "roll", 8000),
            (4, "Aksesoris Lain", "pcs", 2000),
            (5, "Kemasan", "pcs", 1500)
        ]
    
    def record_packing(self, product_name: str, pack_size: int, quantity: int, pack_cost: float):
        """Record packing process"""
        cursor = self.conn.cursor()
        
        try:
            total_items = pack_size * quantity
            total_cost = pack_cost * quantity
            
            # Update stock (reduce loose items, add packed items)
            cursor.execute('''
                UPDATE stock SET quantity = quantity - ?
                WHERE item_type = 'finished' AND item_name = ? AND size IS NULL
            ''', (total_items, product_name))
            
            # Add packed items
            packed_product_name = f"{product_name} Pack {pack_size}pcs"
            cursor.execute('''
                INSERT OR REPLACE INTO stock (item_type, item_name, size, quantity)
                VALUES ('finished', ?, 'PACKED', COALESCE(
                    (SELECT quantity FROM stock WHERE item_type='finished' AND item_name=? AND size='PACKED'), 0
                ) + ?)
            ''', (packed_product_name, packed_product_name, quantity))
            
            # Record packing cost
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, quantity, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', ('expense', 'packing', total_cost, quantity, f"Packing {quantity} pack @ {pack_size}pcs"))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_production_summary(self, days: int = 30):
        """Get production summary"""
        cursor = self.conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT product_name, size, SUM(quantity_produced), SUM(total_cost)
            FROM production_batches 
            WHERE DATE(created_at) >= ?
            GROUP BY product_name, size
        ''', (start_date,))
        
        return cursor.fetchall()
