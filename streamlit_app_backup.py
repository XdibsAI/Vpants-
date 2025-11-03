import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import authentication
try:
    from auth import check_password, get_current_user, logout
    AUTH_AVAILABLE = True
except ImportError as e:
    AUTH_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="VPants - Sistem Pembukuan & Stok Otomatis",
    page_icon="👙",
    layout="wide"
)

# Check authentication
if AUTH_AVAILABLE:
    if not check_password():
        st.stop()
else:
    st.warning("⚠️ Authentication tidak tersedia")

# Import services
try:
    from config.database import init_database
    from services.finance_service import FinanceService
    from services.stock_service import StockService
    from services.stock_management_service import StockManagementService
    from services.initial_setup_service import InitialSetupService
    from services.report_service import ReportService
    from services.simple_production_service import SimpleProductionService
    from services.sales_service import SalesService
    from models.transaction import Transaction
    from models.stock import StockItem
    from utils.helpers import format_currency
    SERVICES_AVAILABLE = True
except ImportError as e:
    st.error(f"Error: {e}")
    SERVICES_AVAILABLE = False

# Initialize services
if SERVICES_AVAILABLE:
    try:
        init_database()
        finance_service = FinanceService()
        stock_service = StockService()
        stock_management = StockManagementService()
        setup_service = InitialSetupService()
        report_service = ReportService()
        production_service = SimpleProductionService()
        sales_service = SalesService()
    except Exception as e:
        st.error(f"Initialization error: {e}")
        SERVICES_AVAILABLE = False

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #667eea;
    text-align: center;
    margin-bottom: 2rem;
}
.card {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 4px solid #667eea;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h3 style="color: #667eea;">VPants</h3>
    <p style="color: #764ba2; font-weight: bold;">SMART WOMEN</p>
    <p style="font-size: 0.8rem; color: #666;">Cp: 085157149669</p>
</div>
""", unsafe_allow_html=True)

# User info
if AUTH_AVAILABLE:
    st.sidebar.markdown(f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <p style="margin: 0; font-size: 0.9rem;">
            <strong>User:</strong> {get_current_user().title()}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

# Navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Pilih Menu:",
    ["🏠 Dashboard", "🏭 Produksi", "💰 Penjualan", "📦 Stok", "📈 Laporan", "⚙️ Lainnya"]
)

# Header
st.markdown('<div class="main-header">👙 VPants - Sistem Sederhana</div>', unsafe_allow_html=True)

if not SERVICES_AVAILABLE:
    st.error("❌ System services tidak tersedia")
    st.stop()

# Dashboard
if page == "🏠 Dashboard":
    col1, col2, col3 = st.columns(3)
    
    # Current balance
    balance = finance_service.get_current_balance()
    with col1:
        st.metric("Saldo Saat Ini", format_currency(balance))
    
    # Financial summary
    summary = report_service.get_financial_summary()
    if summary:
        with col2:
            st.metric("Total Pemasukan", format_currency(summary['total_income']))
        with col3:
            st.metric("Total Pengeluaran", format_currency(summary['total_expenses']))
    
    # Stock overview
    st.subheader("📊 Ringkasan Stok")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**📦 Bahan Siap Jahit:**")
        materials = stock_service.get_stock_levels('material')
        if materials:
            for material in materials:
                quantity = material[3]
                status = "🟢" if quantity > 20 else "🟡" if quantity > 10 else "🔴"
                st.write(f"{status} {material[1]} {material[2] or ''}: **{quantity}** pcs")
        else:
            st.info("Belum ada stok bahan")
    
    with col2:
        st.write("**👙 Barang Jadi:**")
        finished = stock_service.get_stock_levels('finished')
        if finished:
            for item in finished:
                quantity = item[3]
                status = "🟢" if quantity > 15 else "🟡" if quantity > 5 else "🔴"
                st.write(f"{status} {item[1]} {item[2] or ''}: **{quantity}** pcs")
        else:
            st.info("Belum ada barang jadi")
    
    # Recent transactions
    st.subheader("📋 Aktivitas Terbaru")
    daily_report = report_service.get_daily_profit()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pemasukan Hari Ini", format_currency(daily_report['income']))
    with col2:
        st.metric("Pengeluaran Hari Ini", format_currency(daily_report['expenses']))
    with col3:
        profit_color = "green" if daily_report['profit'] >= 0 else "red"
        st.markdown(f"**Profit Hari Ini:** <span style='color: {profit_color}'>{format_currency(daily_report['profit'])}</span>", unsafe_allow_html=True)
    with col4:
        st.metric("Transaksi Hari Ini", daily_report['transaction_count'])

# Produksi
elif page == "🏭 Produksi":
    st.header("🏭 Sistem Produksi")
    
    tab1, tab2 = st.tabs(["📝 Input Produksi", "📦 Proses Packing"])
    
    with tab1:
        st.subheader("Produksi Barang Jadi")
        
        with st.form("simple_production"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_type = st.selectbox("Jenis Produk", ["Celana Dalam VPants", "Celana Pembalut VPants"])
                size = st.selectbox("Ukuran", ["S", "M", "L", "XL"])
                quantity = st.number_input("Jumlah Produksi", min_value=1, value=10)
            
            with col2:
                cost_per_piece = st.number_input("Biaya per pcs (termasuk bahan)", min_value=0, value=35000)
                total_cost = cost_per_piece * quantity
                st.info(f"**Total Biaya:** {format_currency(total_cost)}")
            
            notes = st.text_input("Catatan Produksi")
            
            if st.form_submit_button("🚀 Simpan Produksi"):
                try:
                    production_service.record_production(product_type, size, quantity, cost_per_piece)
                    st.success(f"✅ Berhasil produksi {quantity} pcs {product_type} {size}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with tab2:
        st.subheader("Proses Packing")
        
        with st.form("packing_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_type = st.selectbox("Produk untuk Packing", ["Celana Dalam VPants"])
                pack_size = st.selectbox("Ukuran Pack", [1, 3, 5, 10])
                quantity_packs = st.number_input("Jumlah Pack", min_value=1, value=5)
            
            with col2:
                pack_cost = st.number_input("Biaya Packing per pack", min_value=0, value=5000)
                total_items = pack_size * quantity_packs
                total_cost = pack_cost * quantity_packs
                
                st.info(f"""
                **Detail Packing:**
                - Total items: {total_items} pcs
                - Total biaya: {format_currency(total_cost)}
                """)
            
            if st.form_submit_button("📦 Proses Packing"):
                try:
                    production_service.record_packing(product_type, pack_size, quantity_packs, pack_cost)
                    st.success(f"✅ Berhasil packing {quantity_packs} pack @ {pack_size}pcs")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Penjualan
elif page == "💰 Penjualan":
    st.header("💰 Sistem Penjualan")
    
    tab1, tab2 = st.tabs(["🛒 Penjualan Retail", "📦 Penjualan Pack"])
    
    with tab1:
        st.subheader("Penjualan Retail")
        
        # Get available products
        products = sales_service.get_available_products()
        
        with st.form("retail_sale"):
            col1, col2 = st.columns(2)
            
            with col1:
                if products:
                    product_options = [f"{p[0]} {p[1]} - {format_currency(p[2])} (Stok: {p[3] or 0})" for p in products]
                    selected_product = st.selectbox("Pilih Produk", product_options)
                    
                    # Extract product info
                    product_parts = selected_product.split(' - ')[0].split(' ')
                    product_name = ' '.join(product_parts[:-1])
                    product_size = product_parts[-1]
                    
                    quantity = st.number_input("Jumlah", min_value=1, value=1)
                    unit_price = st.number_input("Harga per pcs", min_value=0, value=75000)
                else:
                    st.warning("Tidak ada produk tersedia")
                    product_name = ""
                    product_size = ""
                    quantity = 1
                    unit_price = 0
            
            with col2:
                discount = st.number_input("Diskon (%)", min_value=0, max_value=100, value=0)
                payment_method = st.selectbox("Metode Bayar", ["Cash", "Transfer", "Shopee", "Tokopedia"])
                customer_notes = st.text_input("Catatan")
                
                total_amount = (unit_price * quantity) * (1 - discount/100)
                st.info(f"**Total Penjualan:** {format_currency(total_amount)}")
            
            if st.form_submit_button("💳 Simpan Penjualan"):
                try:
                    sales_service.record_sale(product_name, product_size, quantity, unit_price, discount, payment_method, customer_notes)
                    st.success(f"✅ Penjualan {quantity} pcs {product_name} {product_size} berhasil dicatat!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with tab2:
        st.subheader("Penjualan Pack")
        
        with st.form("pack_sale"):
            col1, col2 = st.columns(2)
            
            with col1:
                pack_type = st.selectbox("Jenis Pack", [
                    "Celana Dalam Pack 3pcs",
                    "Celana Dalam Pack 5pcs", 
                    "Celana Dalam Pack 10pcs"
                ])
                quantity = st.number_input("Jumlah Pack", min_value=1, value=1)
                
                # Set prices based on pack type
                if "3pcs" in pack_type:
                    unit_price = 200000
                elif "5pcs" in pack_type:
                    unit_price = 300000
                else:
                    unit_price = 550000
                
                st.write(f"Harga per pack: {format_currency(unit_price)}")
            
            with col2:
                discount = st.number_input("Diskon Pack (%)", min_value=0, max_value=100, value=0)
                payment_method = st.selectbox("Metode Pembayaran", ["Cash", "Transfer", "Shopee", "Tokopedia"])
                customer_notes = st.text_input("Catatan Pelanggan")
                
                total_amount = (unit_price * quantity) * (1 - discount/100)
                st.info(f"**Total Penjualan:** {format_currency(total_amount)}")
            
            if st.form_submit_button("📦 Simpan Penjualan Pack"):
                try:
                    sales_service.record_pack_sale(pack_type, quantity, unit_price, discount, payment_method, customer_notes)
                    st.success(f"✅ Penjualan {quantity} pack {pack_type} berhasil dicatat!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Stok
elif page == "📦 Stok":
    st.header("📦 Management Stok")
    
    tab1, tab2 = st.tabs(["📊 Lihat Stok", "✏️ Update Stok"])
    
    with tab1:
        st.subheader("Stok Saat Ini")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📦 Bahan Mentah:**")
            materials = stock_service.get_stock_levels('material')
            if materials:
                df_materials = pd.DataFrame(materials, columns=['Type', 'Nama', 'Size', 'Quantity'])
                st.dataframe(df_materials[['Nama', 'Size', 'Quantity']], hide_index=True)
            else:
                st.info("Belum ada stok bahan")
        
        with col2:
            st.write("**👙 Barang Jadi:**")
            finished = stock_service.get_stock_levels('finished')
            if finished:
                df_finished = pd.DataFrame(finished, columns=['Type', 'Nama', 'Size', 'Quantity'])
                st.dataframe(df_finished[['Nama', 'Size', 'Quantity']], hide_index=True)
            else:
                st.info("Belum ada barang jadi")
    
    with tab2:
        st.subheader("Update Stok Manual")
        
        with st.form("manual_stock"):
            col1, col2 = st.columns(2)
            
            with col1:
                item_type = st.selectbox("Jenis Item", ["Bahan Mentah", "Barang Jadi"])
                item_name = st.text_input("Nama Item")
            
            with col2:
                if item_type == "Barang Jadi":
                    size = st.selectbox("Ukuran", ["S", "M", "L", "XL", "PACKED"])
                else:
                    size = st.selectbox("Ukuran", ["S", "M", "L", "XL", "UMUM"])
                quantity = st.number_input("Quantity", value=0)
                adjustment_type = st.selectbox("Tipe Adjustment", ["Tambah", "Kurangi"])
            
            notes = st.text_input("Catatan")
            
            if st.form_submit_button("💾 Update Stok"):
                try:
                    final_quantity = quantity if adjustment_type == "Tambah" else -quantity
                    stock_type = "material" if item_type == "Bahan Mentah" else "finished"
                    
                    stock_item = StockItem(stock_type, item_name, final_quantity, size)
                    stock_service.update_stock(stock_item)
                    
                    st.success("✅ Stok berhasil diupdate!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Laporan
elif page == "📈 Laporan":
    st.header("📈 Laporan & Analytics")
    
    tab1, tab2, tab3 = st.tabs(["💰 Keuangan", "📊 Penjualan", "📦 Stok"])
    
    with tab1:
        st.subheader("Laporan Keuangan")
        
        # Financial summary
        summary = report_service.get_financial_summary()
        if summary:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Saldo Saat Ini", format_currency(summary['current_balance']))
            with col2:
                st.metric("Total Pemasukan", format_currency(summary['total_income']))
            with col3:
                st.metric("Total Pengeluaran", format_currency(summary['total_expenses']))
            with col4:
                st.metric("Total Transaksi", summary['income_transactions'] + summary['expense_transactions'])
        
        # Daily profit
        st.subheader("Profit Harian")
        date_input = st.date_input("Pilih Tanggal", datetime.now())
        
        if st.button("Generate Laporan Harian"):
            daily_report = report_service.get_daily_profit(date_input)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pemasukan", format_currency(daily_report['income']))
            with col2:
                st.metric("Pengeluaran", format_currency(daily_report['expenses']))
            with col3:
                profit_color = "green" if daily_report['profit'] >= 0 else "red"
                st.markdown(f"**Profit:** <span style='color: {profit_color}'>{format_currency(daily_report['profit'])}</span>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Laporan Penjualan")
        
        days = st.slider("Tampilkan data berapa hari terakhir?", 7, 90, 30)
        
        if st.button("Generate Laporan Penjualan"):
            sales_data = report_service.get_sales_report(days)
            
            if sales_data:
                df_sales = pd.DataFrame(sales_data, columns=['Tanggal', 'Jumlah Transaksi', 'Total Penjualan', 'Total Quantity'])
                df_sales['Total Penjualan'] = df_sales['Total Penjualan'].apply(format_currency)
                st.dataframe(df_sales, hide_index=True)
                
                # Summary
                total_sales = sum(row[2] for row in sales_data)
                total_quantity = sum(row[3] for row in sales_data)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Penjualan Period", format_currency(total_sales))
                with col2:
                    st.metric("Total Quantity Terjual", f"{total_quantity} pcs")
            else:
                st.info("Tidak ada data penjualan dalam periode ini")
    
    with tab3:
        st.subheader("Laporan Stok")
        
        stock_report = report_service.get_stock_report()
        
        if stock_report:
            df_stock = pd.DataFrame(stock_report, columns=['Jenis', 'Nama', 'Size', 'Quantity', 'Status'])
            st.dataframe(df_stock, hide_index=True)
            
            # Stock alerts
            low_stock = [item for item in stock_report if item[4] == 'LOW']
            if low_stock:
                st.warning("🚨 Stok Menipis:")
                for item in low_stock:
                    st.write(f"- {item[1]} {item[2] or ''}: {item[3]} pcs")
        else:
            st.info("Tidak ada data stok")

# Lainnya
elif page == "⚙️ Lainnya":
    st.header("⚙️ Pengaturan & Tools")
    
    tab1, tab2 = st.tabs(["🛠️ Tools", "📝 Setup Awal"])
    
    with tab1:
        st.subheader("System Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Database", type="secondary"):
                try:
                    init_database()
                    st.success("✅ Database berhasil direset!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            
            if st.button("📤 Export Data", type="secondary"):
                st.info("Fitur export data akan segera tersedia")
        
        with col2:
            if st.button("🔄 Refresh Cache", type="secondary"):
                st.rerun()
    
    with tab2:
        st.subheader("Setup Awal Sistem")
        
        st.info("""
        **Instruksi Setup:**
        1. Set saldo awal bisnis
        2. Input stok bahan mentah awal  
        3. Mulai input produksi dan penjualan
        """)
        
        with st.form("initial_setup"):
            initial_balance = st.number_input("Saldo Awal (Rp)", min_value=0, value=5000000)
            
            if st.form_submit_button("💾 Set Saldo Awal"):
                try:
                    setup_service.setup_initial_balance(initial_balance)
                    st.success(f"✅ Saldo awal berhasil diset: {format_currency(initial_balance)}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center;">
    <p style="font-size: 0.8rem; color: #666;">
        <strong>VPants v2.0</strong><br>
        Sistem Sederhana
    </p>
</div>
""", unsafe_allow_html=True)
