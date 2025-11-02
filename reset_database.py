#!/usr/bin/env python3
"""
Reset database dengan schema yang updated
"""
import os
from config.database import init_database

def main():
    print("🔄 Resetting database dengan constraint yang diperbaiki...")
    
    # Hapus file database lama jika ada
    db_path = "data/vpants.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ Database lama dihapus")
    
    # Inisialisasi database baru
    init_database()
    print("✅ Database baru dibuat dengan constraint yang diperbaiki")
    print("🎯 Transaction types yang didukung: sale, purchase, expense, withdrawal, se_income, stock_adjustment, initial_balance")

if __name__ == "__main__":
    main()
