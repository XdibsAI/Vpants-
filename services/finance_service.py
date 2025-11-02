import sqlite3
from config.database import get_connection
from models.transaction import Transaction
from utils.helpers import safe_float

class FinanceService:
    def __init__(self):
        self.conn = get_connection()
    
    def update_balance(self, transaction: Transaction):
        """Update balance based on transaction type"""
        cursor = self.conn.cursor()
        
        try:
            # Get current balance
            cursor.execute("SELECT current_balance, total_income, total_expenses FROM finance ORDER BY last_updated DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                current_balance, total_income, total_expenses = result
            else:
                current_balance, total_income, total_expenses = 0, 0, 0
            
            # Ensure values are safe
            current_balance = safe_float(current_balance)
            total_income = safe_float(total_income)
            total_expenses = safe_float(total_expenses)
            transaction_amount = safe_float(transaction.amount)
            
            # Update based on transaction type
            if transaction.type in ['sale', 'se_income', 'initial_balance']:
                new_balance = current_balance + transaction_amount
                if transaction.type != 'initial_balance':  # Don't count initial balance as income
                    total_income += transaction_amount
            elif transaction.type in ['purchase', 'expense', 'withdrawal']:
                if transaction.type == 'withdrawal':
                    # Include withdrawal fee of Rp 3,000
                    total_amount = transaction_amount + 3000
                    new_balance = current_balance - total_amount
                    total_expenses += total_amount
                else:
                    new_balance = current_balance - transaction_amount
                    total_expenses += transaction_amount
            elif transaction.type == 'stock_adjustment':
                # Stock adjustments don't affect balance
                new_balance = current_balance
            else:
                new_balance = current_balance
            
            # Update finance table
            cursor.execute('''
                INSERT INTO finance (current_balance, total_income, total_expenses)
                VALUES (?, ?, ?)
            ''', (new_balance, total_income, total_expenses))
            
            # Insert transaction record
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, quantity, size, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction.type, transaction.category, transaction_amount, 
                  transaction.quantity, transaction.size, transaction.notes))
            
            self.conn.commit()
            return new_balance
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_current_balance(self) -> float:
        """Get current balance"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT current_balance FROM finance ORDER BY last_updated DESC LIMIT 1")
        result = cursor.fetchone()
        return safe_float(result[0]) if result else 0
    
    def get_financial_summary(self):
        """Get financial summary"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                COALESCE(current_balance, 0),
                COALESCE(total_income, 0),
                COALESCE(total_expenses, 0),
                (SELECT COUNT(*) FROM transactions WHERE type IN ('sale', 'se_income')) as total_income_transactions,
                (SELECT COUNT(*) FROM transactions WHERE type IN ('purchase', 'expense', 'withdrawal')) as total_expense_transactions
            FROM finance 
            ORDER BY last_updated DESC LIMIT 1
        ''')
        result = cursor.fetchone()
        
        if result:
            return (
                safe_float(result[0]),  # current_balance
                safe_float(result[1]),  # total_income
                safe_float(result[2]),  # total_expenses
                result[3] or 0,         # income_transactions
                result[4] or 0          # expense_transactions
            )
        else:
            return (0, 0, 0, 0, 0)
