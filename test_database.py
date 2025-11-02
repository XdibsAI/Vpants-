#!/usr/bin/env python3
"""
Test database constraints
"""
from config.database import get_connection

def test_transaction_types():
    """Test semua transaction types yang diizinkan"""
    conn = get_connection()
    cursor = conn.cursor()
    
    test_transactions = [
        ('sale', 'Penjualan test', 100000, 'Test sale'),
        ('purchase', 'Pembelian test', 50000, 'Test purchase'),
        ('expense', 'Biaya test', 20000, 'Test expense'),
        ('withdrawal', 'Penarikan test', 100000, 'Test withdrawal'),
        ('se_income', 'Shopee test', 80000, 'Test shopee'),
        ('stock_adjustment', 'Stock test', 0, 'Test stock'),
        ('initial_balance', 'Setup test', 1000000, 'Test initial')
    ]
    
    print("🧪 Testing transaction types...")
    
    for i, (t_type, category, amount, notes) in enumerate(test_transactions):
        try:
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, notes)
                VALUES (?, ?, ?, ?)
            ''', (t_type, category, amount, notes))
            print(f"✅ {t_type}: SUCCESS")
        except Exception as e:
            print(f"❌ {t_type}: FAILED - {e}")
    
    conn.commit()
    
    # Verify inserts
    cursor.execute('SELECT type, COUNT(*) FROM transactions GROUP BY type')
    results = cursor.fetchall()
    print(f"\n📊 Total transactions by type: {results}")
    
    conn.close()

if __name__ == "__main__":
    test_transaction_types()
