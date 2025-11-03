import sqlite3
import os
from pathlib import Path

DB_PATH = Path("data/vpants.db")
os.makedirs(DB_PATH.parent, exist_ok=True)

def get_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize database tables dengan schema sederhana"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Drop existing tables
    tables = ['transactions', 'stock', 'products', 'raw_materials', 'production_batches', 'finance']
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')
    
    # Products table - simplified
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            size TEXT NOT NULL,
            selling_price DECIMAL(10,2) NOT NULL,
            cost_per_piece DECIMAL(10,2) NOT NULL,
            pieces_per_pack INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN (
                'sale', 'purchase', 'expense', 'withdrawal', 
                'se_income', 'stock_adjustment', 'initial_balance',
                'production', 'packing'
            )),
            category TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            quantity INTEGER,
            size TEXT,
            unit TEXT,
            discount DECIMAL(5,2) DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Stock table - simplified
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('material', 'finished')),
            item_name TEXT NOT NULL,
            size TEXT,
            quantity INTEGER NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Production batches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS production_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            size TEXT NOT NULL,
            quantity_produced INTEGER NOT NULL,
            labor_cost DECIMAL(10,2) NOT NULL,
            materials_cost DECIMAL(10,2) NOT NULL,
            total_cost DECIMAL(10,2) NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # Insert simple products
    simple_products = [
        # Celana Dalam
        ('Celana Dalam VPants', 'S', 75000, 35000, 1),
        ('Celana Dalam VPants', 'M', 75000, 35000, 1),
        ('Celana Dalam VPants', 'L', 75000, 35000, 1),
        ('Celana Dalam VPants', 'XL', 80000, 38000, 1),
        
        # Celana Pembalut
        ('Celana Pembalut VPants', 'S', 85000, 40000, 1),
        ('Celana Pembalut VPants', 'M', 85000, 40000, 1),
        ('Celana Pembalut VPants', 'L', 85000, 40000, 1),
        
        # Packed products
        ('Celana Dalam Pack 3pcs', 'PACKED', 200000, 105000, 3),
        ('Celana Dalam Pack 5pcs', 'PACKED', 300000, 175000, 5),
        ('Celana Dalam Pack 10pcs', 'PACKED', 550000, 350000, 10),
    ]
    
    cursor.executemany('''
        INSERT INTO products (name, size, selling_price, cost_per_piece, pieces_per_pack)
        VALUES (?, ?, ?, ?, ?)
    ''', simple_products)
    
    # Insert initial materials
    initial_materials = [
        ('material', 'Kain Siap Jahit', 'S', 100),
        ('material', 'Kain Siap Jahit', 'M', 100),
        ('material', 'Kain Siap Jahit', 'L', 100),
        ('material', 'Karet Elastis', None, 50),
        ('material', 'Benang', None, 20),
        ('material', 'Kemasan', None, 200),
    ]
    
    cursor.executemany('''
        INSERT INTO stock (item_type, item_name, size, quantity)
        VALUES (?, ?, ?, ?)
    ''', initial_materials)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized dengan sistem sederhana!")

if __name__ == "__main__":
    init_database()
