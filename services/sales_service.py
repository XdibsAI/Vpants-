"""
Sales service for VPants
"""
import sqlite3
from config.database import get_connection
from models.transaction import Transaction

class SalesService:
    def __init__(self):
        self.conn = get_connection()
    
    def record_sale(self, product_name: str, size: str, quantity: int, unit_price: float, 
                   discount: float = 0, payment_method: str = "", notes: str = ""):
        """Record a sale transaction"""
        cursor = self.conn.cursor()
        
        try:
            total_amount = (unit_price * quantity) * (1 - discount/100)
            
            # Record transaction
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, quantity, size, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('sale', 'retail_sale', total_amount, quantity, size, 
                  f"Penjualan {product_name} {size} - {payment_method} - {notes}"))
            
            # Update stock
            cursor.execute('''
                UPDATE stock SET quantity = quantity - ?
                WHERE item_type = 'finished' AND item_name = ? AND size = ?
            ''', (quantity, product_name, size))
            
            # Update finance
            cursor.execute('''
                INSERT INTO finance (current_balance, total_income, total_expenses)
                SELECT 
                    current_balance + ?,
                    total_income + ?,
                    total_expenses
                FROM finance 
                ORDER BY last_updated DESC LIMIT 1
            ''', (total_amount, total_amount))
            
            self.conn.commit()
            return total_amount
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def record_pack_sale(self, pack_name: str, quantity: int, unit_price: float, 
                        discount: float = 0, payment_method: str = "", notes: str = ""):
        """Record pack sale"""
        cursor = self.conn.cursor()
        
        try:
            total_amount = (unit_price * quantity) * (1 - discount/100)
            
            # Record transaction
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, quantity, size, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('sale', 'pack_sale', total_amount, quantity, 'PACKED', 
                  f"Penjualan {pack_name} - {payment_method} - {notes}"))
            
            # Update stock
            cursor.execute('''
                UPDATE stock SET quantity = quantity - ?
                WHERE item_type = 'finished' AND item_name = ? AND size = 'PACKED'
            ''', (quantity, pack_name))
            
            # Update finance
            cursor.execute('''
                INSERT INTO finance (current_balance, total_income, total_expenses)
                SELECT 
                    current_balance + ?,
                    total_income + ?,
                    total_expenses
                FROM finance 
                ORDER BY last_updated DESC LIMIT 1
            ''', (total_amount, total_amount))
            
            self.conn.commit()
            return total_amount
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_available_products(self):
        """Get available products for sale"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT name, size, selling_price, quantity 
            FROM products p
            LEFT JOIN stock s ON p.name = s.item_name AND p.size = s.size
            WHERE s.item_type = 'finished' AND s.quantity > 0
            ORDER BY p.name, p.size
        ''')
        return cursor.fetchall()
