#!/usr/bin/env python3
"""
Script setup awal untuk VPants
"""
from config.database import init_database
from services.initial_setup_service import InitialSetupService
from services.stock_management_service import StockManagementService
from models.stock import StockItem

def main():
    print("🚀 Setting up VPants system...")
    
    # Initialize database
    init_database()
    print("✅ Database initialized")
    
    # Setup services
    setup_service = InitialSetupService()
    stock_service = StockManagementService()
    
    # Setup initial balance
    setup_service.setup_initial_balance(5000000)
    print("✅ Initial balance set: Rp 5,000,000")
    
    # Setup products
    setup_service.setup_initial_products()
    print("✅ Default products setup")
    
    # Setup initial raw materials stock
    raw_materials = [
        StockItem("material", "Kain Waterproof", 100, "meter"),
        StockItem("material", "Kain Polar", 80, "meter"),
        StockItem("material", "Kain Spandex", 60, "meter"),
        StockItem("material", "Kain Diadora", 70, "meter"),
        StockItem("material", "Karet Elastis", 5, "kg"),
        StockItem("material", "Benang", 10, "roll"),
        StockItem("material", "Resleting", 50, "pcs"),
        StockItem("material", "Kancing", 200, "pcs"),
    ]
    
    stock_service.initialize_stock(raw_materials)
    print("✅ Raw materials stock setup")
    
    # Setup initial finished goods stock
    finished_goods = [
        StockItem("finished", "Celana VPants Basic", 20, "S"),
        StockItem("finished", "Celana VPants Basic", 25, "M"),
        StockItem("finished", "Celana VPants Basic", 20, "L"),
        StockItem("finished", "Celana VPants Basic", 15, "XL"),
        StockItem("finished", "Celana VPants Basic", 10, "XXL"),
    ]
    
    stock_service.initialize_stock(finished_goods)
    print("✅ Finished goods stock setup")
    
    print("🎉 Setup completed successfully!")
    print("📱 You can now run: python -m streamlit run app.py")
    print("💡 Open http://localhost:8501 in your browser")

if __name__ == "__main__":
    main()
