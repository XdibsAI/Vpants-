import sqlite3
from datetime import datetime, timedelta
from config.database import get_connection
from models.transaction import Transaction
from utils.helpers import safe_float

class ProductionService:
    def __init__(self):
        self.conn = get_connection()
    
    def record_production(self, product_name: str, size: str, quantity: int, 
                         labor_cost: float, materials_used: list, notes: str = ""):
        """Record production batch dengan materials used"""
        cursor = self.conn.cursor()
        
        try:
            # Calculate materials cost
            materials_cost = 0
            for material in materials_used:
                material_id = material['material_id']
                material_qty = material['quantity']
                
                # Get material cost
                cursor.execute('SELECT cost_per_unit FROM raw_materials WHERE id = ?', (material_id,))
                result = cursor.fetchone()
                if result:
                    materials_cost += result[0] * material_qty
            
            total_cost = labor_cost + materials_cost
            
            # Insert production batch
            cursor.execute('''
                INSERT INTO production_batches 
                (product_name, size, quantity_produced, labor_cost, materials_cost, total_cost, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_name, size, quantity, labor_cost, materials_cost, total_cost, notes))
            
            # Update finished goods stock
            cursor.execute('''
                INSERT OR REPLACE INTO stock (item_type, item_name, size, quantity)
                VALUES ('finished', ?, ?, COALESCE(
                    (SELECT quantity FROM stock WHERE item_type='finished' AND item_name=? AND size=?), 0
                ) + ?)
            ''', (product_name, size, product_name, size, quantity))
            
            # Update raw materials stock (reduce)
            for material in materials_used:
                material_id = material['material_id']
                material_qty = material['quantity']
                
                cursor.execute('''
                    UPDATE stock SET quantity = quantity - ?
                    WHERE item_type = 'material' AND id = ?
                ''', (material_qty, material_id))
            
            # Record labor cost as expense
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, quantity, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', ('expense', 'production_labor', labor_cost, quantity, 
                  f"Ongkos jahit {quantity}pcs {product_name} {size}"))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_production_history(self, days: int = 30):
        """Get production history"""
        cursor = self.conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT product_name, size, quantity_produced, labor_cost, 
                   materials_cost, total_cost, notes, created_at
            FROM production_batches 
            WHERE DATE(created_at) >= ?
            ORDER BY created_at DESC
        ''', (start_date,))
        
        return cursor.fetchall()
    
    def get_raw_materials(self):
        """Get all raw materials"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, unit, cost_per_unit FROM raw_materials ORDER BY name')
        return cursor.fetchall()
