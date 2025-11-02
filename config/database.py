import sqlite3
import os
from pathlib import Path

DB_PATH = Path("data/vpants.db")
os.makedirs(DB_PATH.parent, exist_ok=True)

def get_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize database tables dengan schema baru"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute('DROP TABLE IF EXISTS transactions')
    cursor.execute('DROP TABLE IF EXISTS stock')
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('DROP TABLE IF EXISTS raw_materials')
    cursor.execute('DROP TABLE IF EXISTS production_batches')
    cursor.execute('DROP TABLE IF EXISTS finance')
    
    # Products table
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
    
    # Raw Materials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            unit TEXT NOT NULL,
            cost_per_unit DECIMAL(10,2) NOT NULL,
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
                'production', 'material_purchase'
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
    
    # Stock table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('raw', 'finished', 'material')),
            item_name TEXT NOT NULL,
            size TEXT,
            unit TEXT,
            quantity DECIMAL(10,3) NOT NULL,
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
    
    # Insert default raw materials
    default_materials = [
        ('Kain Waterproof', 'meter', 25000),
        ('Kain Polar', 'meter', 18000),
        ('Kain Spandex', 'meter', 22000),
        ('Kain Diadora', 'meter', 20000),
        ('Karet Elastis', 'kg', 45000),
        ('Benang', 'roll', 15000),
        ('Resleting', 'pcs', 5000),
        ('Kancing', 'pcs', 200)
    ]
    
    cursor.executemany('''
        INSERT INTO raw_materials (name, unit, cost_per_unit)
        VALUES (?, ?, ?)
    ''', default_materials)
    
    # Insert default products - UPDATED untuk celana dalam wanita
    default_products = [
        ('Celana Dalam VPants', 'S', 75000, 35000, 1),
        ('Celana Dalam VPants', 'M', 75000, 35000, 1),
        ('Celana Dalam VPants', 'L', 75000, 35000, 1),
        ('Celana Dalam VPants', 'XL', 80000, 38000, 1),
        ('Celana Dalam VPants', 'XXL', 80000, 38000, 1),
        ('Celana Pembalut VPants', 'S', 85000, 40000, 1),
        ('Celana Pembalut VPants', 'M', 85000, 40000, 1),
        ('Celana Pembalut VPants', 'L', 85000, 40000, 1),
        ('Celana Dalam Premium', 'S', 95000, 45000, 1),
        ('Celana Dalam Premium', 'M', 95000, 45000, 1),
        ('Celana Dalam Premium', 'L', 95000, 45000, 1),
        ('Paket Celana Dalam', 'MIXED', 200000, 105000, 3),
        ('Paket Celana Dalam', 'MIXED', 300000, 175000, 5),
        ('Paket Celana Dalam', 'MIXED', 550000, 350000, 10),
    ]
    
    cursor.executemany('''
        INSERT INTO products (name, size, selling_price, cost_per_piece, pieces_per_pack)
        VALUES (?, ?, ?, ?, ?)
    ''', default_products)
    
    conn.commit()
    conn.close()
    print("✅ Database reinitialized dengan produk celana dalam wanita!")

if __name__ == "__main__":
    init_database()
