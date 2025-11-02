import sqlite3
from config.database import get_connection
from models.transaction import Transaction

class InitialSetupService:
    def __init__(self):
        self.conn = get_connection()
    
    def setup_initial_balance(self, initial_balance):
        """Set initial balance for the business"""
        cursor = self.conn.cursor()
        
        try:
            # Reset finance table
            cursor.execute('DELETE FROM finance')
            cursor.execute('''
                INSERT INTO finance (current_balance, total_income, total_expenses)
                VALUES (?, 0, 0)
            ''', (initial_balance,))
            
            # Log initial balance transaction dengan type yang benar
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, notes)
                VALUES (?, ?, ?, ?)
            ''', ('initial_balance', 'setup', initial_balance, 'Initial capital setup'))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def setup_initial_products(self):
        """Setup initial product catalog"""
        cursor = self.conn.cursor()
        
        initial_products = [
            ('Celana VPants Basic', 'S', 150000, 80000, 1),
            ('Celana VPants Basic', 'M', 150000, 80000, 1),
            ('Celana VPants Basic', 'L', 150000, 80000, 1),
            ('Celana VPants Basic', 'XL', 160000, 85000, 1),
            ('Celana VPants Basic', 'XXL', 160000, 85000, 1),
        ]
        
        try:
            cursor.execute('DELETE FROM products')
            
            for product in initial_products:
                cursor.execute('''
                    INSERT INTO products (name, size, selling_price, cost_per_piece, pieces_per_pack)
                    VALUES (?, ?, ?, ?, ?)
                ''', product)
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_setup_status(self):
        """Check if system has been initialized"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM finance')
        finance_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM products')
        products_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM stock')
        stock_count = cursor.fetchone()[0]
        
        return {
            'finance_initialized': finance_count > 0,
            'products_initialized': products_count > 0,
            'stock_initialized': stock_count > 0
        }
