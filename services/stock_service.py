import sqlite3
from config.database import get_connection
from models.stock import StockItem

class StockService:
    def __init__(self):
        self.conn = get_connection()
    
    def update_stock(self, stock_item: StockItem):
        """Update stock quantity"""
        cursor = self.conn.cursor()
        
        try:
            # Check if stock item exists
            cursor.execute('''
                SELECT id, quantity FROM stock 
                WHERE item_type = ? AND item_name = ? AND size = ?
            ''', (stock_item.item_type, stock_item.item_name, stock_item.size))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing stock
                stock_id, current_quantity = result
                new_quantity = current_quantity + stock_item.quantity
                cursor.execute('''
                    UPDATE stock SET quantity = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_quantity, stock_id))
            else:
                # Insert new stock item
                cursor.execute('''
                    INSERT INTO stock (item_type, item_name, size, quantity)
                    VALUES (?, ?, ?, ?)
                ''', (stock_item.item_type, stock_item.item_name, stock_item.size, stock_item.quantity))
            
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_stock_levels(self, item_type: str = None):
        """Get stock levels with optional filtering"""
        cursor = self.conn.cursor()
        
        if item_type:
            cursor.execute('''
                SELECT item_type, item_name, size, quantity, last_updated
                FROM stock WHERE item_type = ? ORDER BY item_name, size
            ''', (item_type,))
        else:
            cursor.execute('''
                SELECT item_type, item_name, size, quantity, last_updated
                FROM stock ORDER BY item_type, item_name, size
            ''')
        
        return cursor.fetchall()
    
    def get_low_stock_items(self, threshold: int = 10):
        """Get items with low stock"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT item_type, item_name, size, quantity
            FROM stock WHERE quantity <= ? ORDER BY quantity ASC
        ''', (threshold,))
        
        return cursor.fetchall()
