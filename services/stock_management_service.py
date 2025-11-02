import sqlite3
from datetime import datetime
from config.database import get_connection
from models.stock import StockItem
from utils.helpers import safe_float

class StockManagementService:
    def __init__(self):
        self.conn = get_connection()
    
    def initialize_stock(self, stock_items):
        """Initialize stock with multiple items"""
        cursor = self.conn.cursor()
        
        try:
            for item in stock_items:
                cursor.execute('''
                    INSERT OR REPLACE INTO stock (item_type, item_name, size, quantity)
                    VALUES (?, ?, ?, ?)
                ''', (item.item_type, item.item_name, item.size, item.quantity))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_stock_summary(self):
        """Get complete stock summary"""
        cursor = self.conn.cursor()
        
        # Raw materials summary
        cursor.execute('''
            SELECT item_name, SUM(quantity) as total_quantity
            FROM stock 
            WHERE item_type = 'raw'
            GROUP BY item_name
        ''')
        raw_materials = cursor.fetchall() or []
        
        # Finished goods summary by size
        cursor.execute('''
            SELECT size, SUM(quantity) as total_quantity
            FROM stock 
            WHERE item_type = 'finished' AND size IS NOT NULL
            GROUP BY size
        ''')
        finished_goods = cursor.fetchall() or []
        
        # Total stock value estimation
        cursor.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN item_type = 'raw' THEN quantity * 50000 ELSE 0 END), 0) as raw_value,
                COALESCE(SUM(CASE WHEN item_type = 'finished' THEN quantity * 80000 ELSE 0 END), 0) as finished_value
            FROM stock
        ''')
        stock_value = cursor.fetchone()
        
        raw_value = safe_float(stock_value[0]) if stock_value else 0
        finished_value = safe_float(stock_value[1]) if stock_value else 0
        
        return {
            'raw_materials': raw_materials,
            'finished_goods': finished_goods,
            'total_raw_value': raw_value,
            'total_finished_value': finished_value
        }
    
    def adjust_stock(self, item_type, item_name, adjustment, size=None, notes=""):
        """Adjust stock quantity (positive or negative)"""
        cursor = self.conn.cursor()
        
        try:
            # Check current stock
            if size:
                cursor.execute('''
                    SELECT id, quantity FROM stock 
                    WHERE item_type = ? AND item_name = ? AND size = ?
                ''', (item_type, item_name, size))
            else:
                cursor.execute('''
                    SELECT id, quantity FROM stock 
                    WHERE item_type = ? AND item_name = ? AND (size IS NULL OR size = '')
                ''', (item_type, item_name))
            
            result = cursor.fetchone()
            
            if result:
                stock_id, current_quantity = result
                new_quantity = current_quantity + adjustment
                
                if new_quantity < 0:
                    raise ValueError(f"Stock cannot be negative. Current: {current_quantity}, Adjustment: {adjustment}")
                
                cursor.execute('''
                    UPDATE stock SET quantity = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_quantity, stock_id))
            else:
                if adjustment < 0:
                    raise ValueError(f"Cannot reduce stock for non-existent item: {item_name}")
                
                cursor.execute('''
                    INSERT INTO stock (item_type, item_name, size, quantity)
                    VALUES (?, ?, ?, ?)
                ''', (item_type, item_name, size, adjustment))
            
            # Log the adjustment
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, quantity, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', ('stock_adjustment', f'stock_{item_type}', 0, adjustment, 
                  f"Stock adjustment: {item_name} {size or ''} - {notes}"))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_stock_history(self, days=30):
        """Get stock adjustment history"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT type, category, quantity, notes, created_at
            FROM transactions 
            WHERE type = 'stock_adjustment' 
            AND DATE(created_at) >= DATE('now', ?)
            ORDER BY created_at DESC
        ''', (f'-{days} days',))
        
        return cursor.fetchall() or []
    
    def bulk_update_stock(self, updates):
        """Bulk update multiple stock items"""
        cursor = self.conn.cursor()
        
        try:
            for update in updates:
                item_type = update['item_type']
                item_name = update['item_name']
                quantity = update['quantity']
                size = update.get('size')
                
                if size:
                    cursor.execute('''
                        INSERT OR REPLACE INTO stock (item_type, item_name, size, quantity)
                        VALUES (?, ?, ?, ?)
                    ''', (item_type, item_name, size, quantity))
                else:
                    cursor.execute('''
                        INSERT OR REPLACE INTO stock (item_type, item_name, size, quantity)
                        VALUES (?, ?, NULL, ?)
                    ''', (item_type, item_name, quantity))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_all_stock_items(self):
        """Get all stock items for display"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT item_type, item_name, size, quantity, last_updated
            FROM stock 
            ORDER BY item_type, item_name, size
        ''')
        
        return cursor.fetchall() or []
