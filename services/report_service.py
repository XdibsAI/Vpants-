"""
Report service for VPants
"""
import sqlite3
from datetime import datetime, timedelta
from config.database import get_connection
from utils.helpers import format_currency

class ReportService:
    def __init__(self):
        self.conn = get_connection()
    
    def get_daily_profit(self, date: datetime = None):
        """Calculate daily profit"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        
        # Get daily income
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE type IN ('sale', 'se_income') 
            AND DATE(created_at) = ?
        ''', (date_str,))
        
        daily_income = cursor.fetchone()[0] or 0
        
        # Get daily expenses
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE type IN ('purchase', 'expense', 'production', 'packing') 
            AND DATE(created_at) = ?
        ''', (date_str,))
        
        daily_expenses = cursor.fetchone()[0] or 0
        
        # Add withdrawal fees
        cursor.execute('''
            SELECT COUNT(*) 
            FROM transactions 
            WHERE type = 'withdrawal' 
            AND DATE(created_at) = ?
        ''', (date_str,))
        
        withdrawal_count = cursor.fetchone()[0] or 0
        withdrawal_fees = withdrawal_count * 3000
        
        total_expenses = daily_expenses + withdrawal_fees
        daily_profit = daily_income - total_expenses
        
        # Count total transactions for the day
        cursor.execute('''
            SELECT COUNT(*) 
            FROM transactions 
            WHERE DATE(created_at) = ?
        ''', (date_str,))
        
        transaction_count = cursor.fetchone()[0] or 0
        
        return {
            'date': date_str,
            'income': daily_income,
            'expenses': total_expenses,
            'profit': daily_profit,
            'transaction_count': transaction_count
        }
    
    def get_sales_report(self, days: int = 30):
        """Get sales report"""
        cursor = self.conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT 
                strftime('%Y-%m-%d', created_at) as sale_date,
                COUNT(*) as transaction_count,
                SUM(amount) as total_sales,
                SUM(quantity) as total_quantity
            FROM transactions 
            WHERE type = 'sale' 
            AND DATE(created_at) >= ?
            GROUP BY sale_date
            ORDER BY sale_date DESC
        ''', (start_date,))
        
        return cursor.fetchall()
    
    def get_stock_report(self):
        """Get stock report"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT item_type, item_name, size, quantity,
                   CASE 
                       WHEN quantity <= 10 THEN 'LOW'
                       WHEN quantity <= 25 THEN 'MEDIUM' 
                       ELSE 'HIGH'
                   END as stock_level
            FROM stock
            ORDER BY item_type, item_name, size
        ''')
        
        return cursor.fetchall()
    
    def get_financial_summary(self):
        """Get financial summary"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                current_balance,
                total_income,
                total_expenses,
                (SELECT COUNT(*) FROM transactions WHERE type IN ('sale', 'se_income')) as income_count,
                (SELECT COUNT(*) FROM transactions WHERE type IN ('purchase', 'expense', 'withdrawal', 'production', 'packing')) as expense_count
            FROM finance 
            ORDER BY last_updated DESC LIMIT 1
        ''')
        
        result = cursor.fetchone()
        if result:
            return {
                'current_balance': result[0] or 0,
                'total_income': result[1] or 0,
                'total_expenses': result[2] or 0,
                'income_transactions': result[3] or 0,
                'expense_transactions': result[4] or 0
            }
        return None
    
    def get_recent_transactions(self, days: int = 7):
        """Get recent transactions for dashboard"""
        cursor = self.conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT type, category, amount, quantity, size, notes, created_at
            FROM transactions 
            WHERE DATE(created_at) >= ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (start_date,))
        
        return cursor.fetchall()
    
    def get_transaction_history(self, days: int = 7):
        """Alias for get_recent_transactions for compatibility"""
        return self.get_recent_transactions(days)
