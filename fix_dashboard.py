"""
Quick fix for dashboard metrics
"""
import sqlite3
from config.database import get_connection

def fix_dashboard_metrics():
    """Ensure all metrics have safe values"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ensure finance table has proper values
    cursor.execute('''
        UPDATE finance 
        SET current_balance = COALESCE(current_balance, 0),
            total_income = COALESCE(total_income, 0),
            total_expenses = COALESCE(total_expenses, 0)
        WHERE current_balance IS NULL OR total_income IS NULL OR total_expenses IS NULL
    ''')
    
    # Ensure stock table has proper values
    cursor.execute('''
        UPDATE stock 
        SET quantity = COALESCE(quantity, 0)
        WHERE quantity IS NULL
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Dashboard metrics fixed!")

if __name__ == "__main__":
    fix_dashboard_metrics()
