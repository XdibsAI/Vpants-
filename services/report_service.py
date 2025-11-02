import sqlite3
from datetime import datetime, timedelta
from config.database import get_connection
from utils.helpers import safe_float

class ReportService:
    def __init__(self):
        self.conn = get_connection()
    
    def get_daily_profit(self, date: datetime = None):
        """Calculate daily profit"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        
        # Get daily income (sales + shopee income)
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE type IN ('sale', 'se_income') 
            AND DATE(created_at) = ?
        ''', (date_str,))
        
        daily_income = safe_float(cursor.fetchone()[0])
        
        # Get daily expenses (purchases + expenses + withdrawals)
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE type IN ('purchase', 'expense') 
            AND DATE(created_at) = ?
        ''', (date_str,))
        
        daily_expenses = safe_float(cursor.fetchone()[0])
        
        # Add withdrawal fees (Rp 3,000 per withdrawal)
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
        
        # Count total transactions
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
    
    def get_monthly_report(self, year: int = None, month: int = None):
        """Generate monthly report"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        cursor = self.conn.cursor()
        
        # Monthly summary
        cursor.execute('''
            SELECT 
                type,
                COUNT(*) as transaction_count,
                COALESCE(SUM(amount), 0) as total_amount
            FROM transactions 
            WHERE strftime('%Y-%m', created_at) = ?
            GROUP BY type
        ''', (f"{year:04d}-{month:02d}",))
        
        monthly_data = cursor.fetchall() or []
        
        return {
            'year': year,
            'month': month,
            'transactions': monthly_data
        }
    
    def get_transaction_history(self, days: int = 30):
        """Get transaction history for specified days"""
        cursor = self.conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT type, category, amount, quantity, size, notes, created_at
            FROM transactions 
            WHERE DATE(created_at) >= ?
            ORDER BY created_at DESC
        ''', (start_date,))
        
        return cursor.fetchall() or []
