import sqlite3
from config.database import get_connection
from models.transaction import Transaction
from utils.helpers import safe_float

class SalesService:
    def __init__(self):
        self.conn = get_connection()
    
    def record_sale(self, items: list, total_amount: float, discount: float = 0, 
                   notes: str = "", is_pack: bool = False):
        """Record sale dengan support untuk multiple items dan pack sales"""
        cursor = self.conn.cursor()
        
        try:
            # Calculate final amount after discount
            final_amount = total_amount * (1 - discount)
            
            # Record main transaction
            transaction_type = 'sale_pack' if is_pack else 'sale'
            category = 'pack_sale' if is_pack else 'retail_sale'
            
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, discount, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (transaction_type, category, final_amount, discount, notes))
            
            transaction_id = cursor.lastrowid
            
            # Record individual items
            for item in items:
                product_name = item['product_name']
                size = item.get('size')
                quantity = item['quantity']
                unit_price = item.get('unit_price', 0)
                
                # Reduce stock
                if size:
                    cursor.execute('''
                        UPDATE stock SET quantity = quantity - ?
                        WHERE item_type = 'finished' AND item_name = ? AND size = ?
                    ''', (quantity, product_name, size))
                else:
                    cursor.execute('''
                        UPDATE stock SET quantity = quantity - ?
                        WHERE item_type = 'finished' AND item_name = ? AND size IS NULL
                    ''', (quantity, product_name))
                
                # Record sale item detail
                cursor.execute('''
                    INSERT INTO transaction_items (transaction_id, product_name, size, quantity, unit_price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (transaction_id, product_name, size, quantity, unit_price))
            
            # Update finance
            cursor.execute('''
                INSERT INTO finance (current_balance, total_income, total_expenses)
                SELECT 
                    current_balance + ?,
                    total_income + ?,
                    total_expenses
                FROM finance 
                ORDER BY last_updated DESC LIMIT 1
            ''', (final_amount, final_amount))
            
            self.conn.commit()
            return final_amount
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def apply_bonus_items(self, main_transaction_id: int, bonus_items: list):
        """Apply bonus items untuk pembelian dalam jumlah banyak"""
        cursor = self.conn.cursor()
        
        try:
            for bonus in bonus_items:
                product_name = bonus['product_name']
                size = bonus.get('size')
                quantity = bonus['quantity']
                
                # Reduce stock for bonus items
                if size:
                    cursor.execute('''
                        UPDATE stock SET quantity = quantity - ?
                        WHERE item_type = 'finished' AND item_name = ? AND size = ?
                    ''', (quantity, product_name, size))
                else:
                    cursor.execute('''
                        UPDATE stock SET quantity = quantity - ?
                        WHERE item_type = 'finished' AND item_name = ? AND size IS NULL
                    ''', (quantity, product_name))
                
                # Record bonus
                cursor.execute('''
                    INSERT INTO transaction_bonus (transaction_id, product_name, size, quantity)
                    VALUES (?, ?, ?, ?)
                ''', (main_transaction_id, product_name, size, quantity))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
