import sqlite3
import os
from pathlib import Path

DB_PATH = Path("data/vpants.db")
os.makedirs(DB_PATH.parent, exist_ok=True)

def get_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Drop and recreate tables with updated constraints
    cursor.execute('DROP TABLE IF EXISTS transactions')
    cursor.execute('DROP TABLE IF EXISTS stock')
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('DROP TABLE IF EXISTS finance')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            size TEXT NOT NULL,
            selling_price DECIMAL(10,2) NOT NULL,
            cost_per_piece DECIMAL(10,2) NOT NULL,
            pieces_per_pack INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Transactions table - Updated CHECK constraint
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN (
                'sale', 'purchase', 'expense', 'withdrawal', 
                'se_income', 'stock_adjustment', 'initial_balance'
            )),
            category TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            quantity INTEGER,
            size TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Stock table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('raw', 'finished')),
            item_name TEXT NOT NULL,
            size TEXT,
            quantity INTEGER NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Finance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_balance DECIMAL(10,2) DEFAULT 0,
            total_income DECIMAL(10,2) DEFAULT 0,
            total_expenses DECIMAL(10,2) DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert initial finance record
    cursor.execute('''
        INSERT INTO finance (current_balance, total_income, total_expenses) 
        VALUES (0, 0, 0)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database reinitialized with updated constraints!")

if __name__ == "__main__":
    init_database()
