import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
from PIL import Image
import io

# Import services
from config.database import init_database
from config.brand_config import get_brand_config
from services.finance_service import FinanceService
from services.stock_service import StockService
from services.stock_management_service import StockManagementService
from services.initial_setup_service import InitialSetupService
from services.report_service import ReportService
from models.transaction import Transaction
from models.stock import StockItem
from utils.helpers import format_currency

# Page configuration
st.set_page_config(
    page_title="VPants - Pembukuan & Stok Otomatis",
    page_icon="👖",
    layout="wide"
)

# Initialize database
init_database()

# Initialize services
finance_service = FinanceService()
stock_service = StockService()
stock_management_service = StockManagementService()
setup_service = InitialSetupService()
report_service = ReportService()

# Get brand configuration
brand_config = get_brand_config()

def get_base64_of_image(image_path):
    """Convert image to base64 for HTML display"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def display_logo():
    """Display brand logo and information"""
    logo_base64 = get_base64_of_image(brand_config['logo_path'])
    
    if logo_base64:
        st.sidebar.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <img src="data:image/webp;base64,{logo_base64}" width="120" style="border-radius: 10px;">
            <h3 style="color: {brand_config['primary_color']}; margin: 10px 0 5px 0;">{brand_config['name']}</h3>
            <p style="color: {brand_config['secondary_color']}; font-weight: bold; margin: 0;">{brand_config['slogan']}</p>
            <p style="font-size: 0.8rem; color: #666; margin: 5px 0;">{brand_config['contact']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h3 style="color: {brand_config['primary_color']}; margin: 10px 0 5px 0;">{brand_config['name']}</h3>
            <p style="color: {brand_config['secondary_color']}; font-weight: bold; margin: 0;">{brand_config['slogan']}</p>
            <p style="font-size: 0.8rem; color: #666; margin: 5px 0;">{brand_config['contact']}</p>
        </div>
        """, unsafe_allow_html=True)

# Custom CSS with brand colors
st.markdown(f"""
<style>
    .main-header {{
        font-size: 2.5rem;
        color: {brand_config['primary_color']};
        text-align: center;
        margin-bottom: 2rem;
    }}
    .balance-card {{
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid {brand_config['primary_color']};
    }}
    .profit-positive {{
        color: #00aa00;
        font-weight: bold;
    }}
    .profit-negative {{
        color: #ff0000;
        font-weight: bold;
    }}
    .brand-section {{
        background: linear-gradient(135deg, {brand_config['primary_color']}20, {brand_config['secondary_color']}20);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }}
</style>
""", unsafe_allow_html=True)

# Display logo in sidebar
display_logo()

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Pilih Menu:",
    ["🏠 Dashboard", "💰 Transaksi", "📦 Stok", "⚡ Input Stock Awal", "📈 Laporan", "⚙️ Setup Awal"]
)

# Check setup status
setup_status = setup_service.get_setup_status()

# Show setup warning if not initialized
if not setup_status['finance_initialized'] and page != "⚙️ Setup Awal":
    st.warning("⚠️ Sistem belum diinisialisasi. Silakan buka **Setup Awal** terlebih dahulu.")
    if st.button("Pergi ke Setup Awal"):
        st.experimental_set_query_params(page="Setup Awal")
    st.stop()

# Header
st.markdown(f'<div class="main-header">👖 {brand_config["name"]} - Sistem Pembukuan & Stok</div>', unsafe_allow_html=True)

# Dashboard Page
if page == "🏠 Dashboard":
    col1, col2, col3 = st.columns(3)
    
    # Current Balance
    current_balance = finance_service.get_current_balance()
    with col1:
        st.metric(
            label="Saldo Saat Ini",
            value=format_currency(current_balance),
            delta=None
        )
    
    # Financial Summary
    summary = finance_service.get_financial_summary()
    if summary:
        current_balance, total_income, total_expenses, income_tx, expense_tx = summary
        
        with col2:
            st.metric(
                label="Total Pemasukan",
                value=format_currency(total_income),
                delta=f"{income_tx} transaksi"
            )
        
        with col3:
            st.metric(
                label="Total Pengeluaran",
                value=format_currency(total_expenses),
                delta=f"{expense_tx} transaksi"
            )
    
    # Stock Summary
    st.subheader("📊 Ringkasan Stok")
    stock_summary = stock_management_service.get_stock_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_raw = sum(item[1] for item in stock_summary['raw_materials'])
        st.metric("Bahan Mentah", f"{total_raw} pack")
    
    with col2:
        total_finished = sum(item[1] for item in stock_summary['finished_goods'])
        st.metric("Barang Jadi", f"{total_finished} pcs")
    
    with col3:
        st.metric("Nilai Stok Bahan", format_currency(stock_summary['total_raw_value']))
    
    with col4:
        st.metric("Nilai Stok Jadi", format_currency(stock_summary['total_finished_value']))
    
    # Daily Profit
    st.subheader("💰 Profit Hari Ini")
    daily_profit = report_service.get_daily_profit()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pemasukan Hari Ini", format_currency(daily_profit['income']))
    with col2:
        st.metric("Pengeluaran Hari Ini", format_currency(daily_profit['expenses']))
    with col3:
        profit_class = "profit-positive" if daily_profit['profit'] >= 0 else "profit-negative"
        st.markdown(f"**Profit Hari Ini:** <span class='{profit_class}'>{format_currency(daily_profit['profit'])}</span>", 
                   unsafe_allow_html=True)
    with col4:
        st.metric("Total Transaksi", daily_profit['transaction_count'])
    
    # Recent Transactions
    st.subheader("📋 Transaksi Terbaru")
    recent_transactions = report_service.get_transaction_history(days=7)
    
    if recent_transactions:
        df_recent = pd.DataFrame(recent_transactions, 
                               columns=['Jenis', 'Kategori', 'Amount', 'Qty', 'Size', 'Notes', 'Tanggal'])
        df_recent['Amount'] = df_recent['Amount'].apply(format_currency)
        st.dataframe(df_recent.head(10), use_container_width=True)
    else:
        st.info("Belum ada transaksi dalam 7 hari terakhir.")

# Transaction Page (sama seperti sebelumnya, tetap dipertahankan)
elif page == "💰 Transaksi":
    st.header("💳 Input Transaksi")
    
    transaction_type = st.selectbox(
        "Jenis Transaksi:",
        ["Penjualan", "Pemasukan Shopee", "Bayar Penjahit", "Belanja Bahan", "Penarikan Tunai", "Biaya Lain"]
    )
    
    with st.form("transaction_form"):
        if transaction_type == "Penjualan":
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Jumlah Pemasukan Bersih (Rp)", min_value=0, step=1000)
                quantity = st.number_input("Jumlah Terjual (pcs)", min_value=1, step=1)
            with col2:
                size = st.selectbox("Ukuran", ["S", "M", "L", "XL", "XXL"])
                notes = st.text_input("Catatan (opsional)")
            
        elif transaction_type == "Pemasukan Shopee":
            amount = st.number_input("Jumlah Pemasukan Bersih Setelah Potongan (Rp)", min_value=0, step=1000)
            quantity = None
            size = None
            notes = st.text_input("Catatan (opsional)")
            
        elif transaction_type == "Bayar Penjahit":
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Jumlah Bayaran (Rp)", min_value=0, step=1000)
                quantity = st.number_input("Jumlah pcs yang diselesaikan", min_value=1, step=1)
            with col2:
                size = st.selectbox("Ukuran", ["S", "M", "L", "XL", "XXL"])
                notes = st.text_input("Catatan (opsional)")
            
        elif transaction_type == "Belanja Bahan":
            category = st.selectbox("Jenis Bahan", ["Waterproof", "Polar", "Spandex", "Diadora", "Lainnya"])
            amount = st.number_input("Jumlah Pengeluaran (Rp)", min_value=0, step=1000)
            quantity = st.number_input("Quantity Beli", min_value=1, step=1)
            size = None
            notes = st.text_input("Catatan (opsional)")
            
        elif transaction_type == "Penarikan Tunai":
            amount = st.number_input("Jumlah Penarikan (Rp)", min_value=0, step=1000)
            st.info(f"Biaya admin: Rp 3,000 | Total dikurangi: {format_currency(amount + 3000)}")
            quantity = None
            size = None
            notes = st.text_input("Alasan penarikan (opsional)")
            
        else:  # Biaya Lain
            category = st.selectbox("Jenis Biaya", ["Biaya Admin", "Biaya ATM", "Transportasi", "Lainnya"])
            amount = st.number_input("Jumlah Pengeluaran (Rp)", min_value=0, step=1000)
            quantity = None
            size = None
            notes = st.text_input("Keterangan biaya")
        
        submitted = st.form_submit_button("Simpan Transaksi")
        
        if submitted:
            if amount <= 0:
                st.error("Jumlah transaksi harus lebih dari 0")
            else:
                # Map transaction types
                type_mapping = {
                    "Penjualan": "sale",
                    "Pemasukan Shopee": "se_income", 
                    "Bayar Penjahit": "expense",
                    "Belanja Bahan": "purchase",
                    "Penarikan Tunai": "withdrawal",
                    "Biaya Lain": "expense"
                }
                
                # Map categories
                if transaction_type == "Belanja Bahan":
                    transaction_category = f"Bahan_{category}"
                elif transaction_type == "Biaya Lain":
                    transaction_category = f"Biaya_{category}"
                elif transaction_type == "Bayar Penjahit":
                    transaction_category = "Ongkos_Jahit"
                else:
                    transaction_category = transaction_type.replace(" ", "_")
                
                transaction = Transaction(
                    type=type_mapping[transaction_type],
                    category=transaction_category,
                    amount=amount,
                    quantity=quantity,
                    size=size,
                    notes=notes
                )
                
                try:
                    new_balance = finance_service.update_balance(transaction)
                    
                    # Update stock for relevant transactions
                    if transaction_type == "Bayar Penjahit":
                        # Add finished goods to stock
                        stock_item = StockItem(
                            item_type="finished",
                            item_name="Celana VPants",
                            quantity=quantity,
                            size=size
                        )
                        stock_service.update_stock(stock_item)
                        st.success(f"✅ Berhasil bayar penjahit dan tambah stok {quantity} pcs size {size}")
                        
                    elif transaction_type == "Belanja Bahan":
                        # Add raw materials to stock
                        stock_item = StockItem(
                            item_type="raw", 
                            item_name=category,
                            quantity=quantity,
                            size=None
                        )
                        stock_service.update_stock(stock_item)
                        st.success(f"✅ Berhasil belanja {category} dan tambah stok {quantity} pack")
                    
                    elif transaction_type == "Penjualan":
                        # Reduce finished goods stock
                        stock_item = StockItem(
                            item_type="finished",
                            item_name="Celana VPants", 
                            quantity=-quantity,  # Negative to reduce
                            size=size
                        )
                        stock_service.update_stock(stock_item)
                        st.success(f"✅ Penjualan {quantity} pcs size {size} dicatat")
                    
                    st.success(f"✅ Transaksi berhasil disimpan! Saldo baru: {format_currency(new_balance)}")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Stock Page - Diperbarui dengan modul baru
elif page == "📦 Stok":
    st.header("📊 Management Stok")
    
    tab1, tab2, tab3 = st.tabs(["Lihat Stok", "Update Stok Manual", "Riwayat Stock"])
    
    with tab1:
        st.subheader("Level Stok Saat Ini")
        
        stock_summary = stock_management_service.get_stock_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📦 Bahan Mentah**")
            if stock_summary['raw_materials']:
                df_raw = pd.DataFrame(stock_summary['raw_materials'], columns=['Bahan', 'Quantity'])
                st.dataframe(df_raw, use_container_width=True)
            else:
                st.info("Belum ada stok bahan mentah")
        
        with col2:
            st.write("**👖 Barang Jadi (per Ukuran)**")
            if stock_summary['finished_goods']:
                df_finished = pd.DataFrame(stock_summary['finished_goods'], columns=['Ukuran', 'Quantity'])
                st.dataframe(df_finished, use_container_width=True)
            else:
                st.info("Belum ada stok barang jadi")
        
        # Stock Value
        st.subheader("💰 Nilai Stok Estimasi")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Nilai Bahan Mentah", format_currency(stock_summary['total_raw_value']))
        with col2:
            st.metric("Total Nilai Barang Jadi", format_currency(stock_summary['total_finished_value']))
        
        # Low stock alert
        st.subheader("🚨 Alert Stok Menipis")
        low_stock = stock_service.get_low_stock_items(threshold=10)
        if low_stock:
            for item in low_stock:
                item_type, item_name, size, quantity = item
                st.warning(f"{item_name} {size or ''} - sisa {quantity} (Stok menipis!)")
        else:
            st.success("✅ Semua stok dalam kondisi aman")
    
    with tab2:
        st.subheader("Update Stok Manual")
        
        with st.form("manual_stock_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_type = st.selectbox("Jenis Item", ["Bahan Mentah", "Barang Jadi"])
                item_name = st.text_input("Nama Item")
            with col2:
                if item_type == "Barang Jadi":
                    size = st.selectbox("Ukuran", ["S", "M", "L", "XL", "XXL"])
                else:
                    size = None
                quantity = st.number_input("Quantity (+/- untuk tambah/kurang)", step=1)
            
            notes = st.text_input("Alasan update (opsional)")
            
            submitted = st.form_submit_button("Update Stok")
            
            if submitted:
                try:
                    stock_management_service.adjust_stock(
                        item_type="raw" if item_type == "Bahan Mentah" else "finished",
                        item_name=item_name,
                        adjustment=quantity,
                        size=size,
                        notes=notes
                    )
                    st.success("✅ Stok berhasil diupdate!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("Riwayat Perubahan Stok")
        days = st.slider("Tampilkan riwayat berapa hari terakhir?", 7, 90, 30)
        
        stock_history = stock_management_service.get_stock_history(days)
        
        if stock_history:
            df_history = pd.DataFrame(stock_history, 
                                    columns=['Jenis', 'Kategori', 'Quantity', 'Notes', 'Tanggal'])
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("Belum ada perubahan stok dalam periode ini")

# New Page: Initial Stock Input
elif page == "⚡ Input Stock Awal":
    st.header("⚡ Input Saldo Stock Awal")
    
    st.warning("""
    **Perhatian:** Hanya gunakan menu ini untuk pertama kali setup atau reset stock.
    Perubahan akan langsung mempengaruhi database.
    """)
    
    tab1, tab2 = st.tabs(["Input Bahan Mentah", "Input Barang Jadi"])
    
    with tab1:
        st.subheader("📦 Input Stock Bahan Mentah Awal")
        
        with st.form("initial_raw_stock"):
            st.write("**Bahan Baku:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                waterproof_qty = st.number_input("Waterproof (pack)", min_value=0, value=0)
                polar_qty = st.number_input("Polar (pack)", min_value=0, value=0)
            
            with col2:
                spandex_qty = st.number_input("Spandex (pack)", min_value=0, value=0)
                diadora_qty = st.number_input("Diadora (pack)", min_value=0, value=0)
                other_qty = st.number_input("Lainnya (pack)", min_value=0, value=0)
                other_name = st.text_input("Nama bahan lainnya")
            
            submitted = st.form_submit_button("Simpan Stock Bahan Mentah")
            
            if submitted:
                raw_items = []
                
                if waterproof_qty > 0:
                    raw_items.append(StockItem("raw", "Waterproof", waterproof_qty))
                if polar_qty > 0:
                    raw_items.append(StockItem("raw", "Polar", polar_qty))
                if spandex_qty > 0:
                    raw_items.append(StockItem("raw", "Spandex", spandex_qty))
                if diadora_qty > 0:
                    raw_items.append(StockItem("raw", "Diadora", diadora_qty))
                if other_qty > 0 and other_name:
                    raw_items.append(StockItem("raw", other_name, other_qty))
                
                if raw_items:
                    try:
                        stock_management_service.initialize_stock(raw_items)
                        st.success(f"✅ Berhasil menyimpan {len(raw_items)} jenis bahan mentah!")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Tidak ada bahan yang diinput")
    
    with tab2:
        st.subheader("👖 Input Stock Barang Jadi Awal")
        
        with st.form("initial_finished_stock"):
            st.write("**Stock Awal per Ukuran:**")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                size_s = st.number_input("Size S (pcs)", min_value=0, value=0)
            with col2:
                size_m = st.number_input("Size M (pcs)", min_value=0, value=0)
            with col3:
                size_l = st.number_input("Size L (pcs)", min_value=0, value=0)
            with col4:
                size_xl = st.number_input("Size XL (pcs)", min_value=0, value=0)
            with col5:
                size_xxl = st.number_input("Size XXL (pcs)", min_value=0, value=0)
            
            submitted = st.form_submit_button("Simpan Stock Barang Jadi")
            
            if submitted:
                finished_items = []
                
                if size_s > 0:
                    finished_items.append(StockItem("finished", "Celana VPants", size_s, "S"))
                if size_m > 0:
                    finished_items.append(StockItem("finished", "Celana VPants", size_m, "M"))
                if size_l > 0:
                    finished_items.append(StockItem("finished", "Celana VPants", size_l, "L"))
                if size_xl > 0:
                    finished_items.append(StockItem("finished", "Celana VPants", size_xl, "XL"))
                if size_xxl > 0:
                    finished_items.append(StockItem("finished", "Celana VPants", size_xxl, "XXL"))
                
                if finished_items:
                    try:
                        stock_management_service.initialize_stock(finished_items)
                        st.success(f"✅ Berhasil menyimpan stock {sum(item.quantity for item in finished_items)} pcs barang jadi!")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Tidak ada barang jadi yang diinput")

# Laporan Page (tetap sama)
elif page == "📈 Laporan":
    st.header("📊 Laporan Keuangan")
    
    tab1, tab2, tab3 = st.tabs(["Harian", "Bulanan", "Riwayat Transaksi"])
    
    with tab1:
        st.subheader("Laporan Profit Harian")
        date_input = st.date_input("Pilih Tanggal", datetime.now())
        
        if st.button("Generate Laporan Harian"):
            daily_report = report_service.get_daily_profit(date_input)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Pemasukan", format_currency(daily_report['income']))
            with col2:
                st.metric("Pengeluaran", format_currency(daily_report['expenses']))
            with col3:
                st.metric("Profit", format_currency(daily_report['profit']))
            with col4:
                st.metric("Jumlah Transaksi", daily_report['transaction_count'])
    
    with tab2:
        st.subheader("Laporan Bulanan")
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Tahun", min_value=2020, max_value=2030, value=datetime.now().year)
        with col2:
            month = st.selectbox("Bulan", range(1, 13), format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
        
        if st.button("Generate Laporan Bulanan"):
            monthly_report = report_service.get_monthly_report(year, month)
            
            st.write(f"### Laporan {monthly_report['month']}/{monthly_report['year']}")
            
            if monthly_report['transactions']:
                df_monthly = pd.DataFrame(monthly_report['transactions'], 
                                        columns=['Jenis', 'Jumlah Transaksi', 'Total Amount'])
                df_monthly['Total Amount'] = df_monthly['Total Amount'].apply(format_currency)
                st.dataframe(df_monthly, use_container_width=True)
            else:
                st.info("Tidak ada transaksi untuk periode ini")
    
    with tab3:
        st.subheader("Riwayat Transaksi Lengkap")
        days = st.slider("Tampilkan transaksi berapa hari terakhir?", 7, 90, 30)
        
        transactions = report_service.get_transaction_history(days)
        
        if transactions:
            df_transactions = pd.DataFrame(transactions, 
                                         columns=['Jenis', 'Kategori', 'Amount', 'Qty', 'Size', 'Notes', 'Tanggal'])
            df_transactions['Amount'] = df_transactions['Amount'].apply(format_currency)
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                filter_type = st.selectbox("Filter Jenis Transaksi", ["Semua"] + list(df_transactions['Jenis'].unique()))
            with col2:
                filter_category = st.selectbox("Filter Kategori", ["Semua"] + list(df_transactions['Kategori'].unique()))
            
            # Apply filters
            filtered_df = df_transactions
            if filter_type != "Semua":
                filtered_df = filtered_df[filtered_df['Jenis'] == filter_type]
            if filter_category != "Semua":
                filtered_df = filtered_df[filtered_df['Kategori'] == filter_category]
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # Export option
            if st.button("📥 Export ke CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"transaksi_vpants_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info(f"Tidak ada transaksi dalam {days} hari terakhir")

# Setup Awal Page
elif page == "⚙️ Setup Awal":
    st.header("⚙️ Setup Awal Sistem")
    
    setup_status = setup_service.get_setup_status()
    
    st.info("""
    **Instruksi:** 
    1. Set saldo awal terlebih dahulu
    2. Setup produk (opsional)
    3. Input stock awal di menu **Input Stock Awal**
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("💰 Saldo Awal")
        with st.form("initial_balance"):
            initial_balance = st.number_input("Saldo Awal (Rp)", min_value=0, value=1000000, step=100000)
            submitted = st.form_submit_button("Set Saldo Awal")
            
            if submitted:
                try:
                    setup_service.setup_initial_balance(initial_balance)
                    st.success(f"✅ Saldo awal berhasil diset: {format_currency(initial_balance)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("📝 Setup Produk")
        st.write("Setup daftar produk default")
        if st.button("Setup Produk Default"):
            try:
                setup_service.setup_initial_products()
                st.success("✅ Produk default berhasil disetup!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col3:
        st.subheader("📊 Status Sistem")
        st.write(f"Saldo: {'✅' if setup_status['finance_initialized'] else '❌'}")
        st.write(f"Produk: {'✅' if setup_status['products_initialized'] else '❌'}")
        st.write(f"Stock: {'✅' if setup_status['stock_initialized'] else '❌'}")
        
        if all(setup_status.values()):
            st.success("✅ Sistem sudah siap digunakan!")
        else:
            st.warning("⚠️ Beberapa komponen belum disetup")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div class="brand-section">
    <p style="font-size: 0.8rem; text-align: center;">
        <strong>{brand_config['name']} System</strong><br>
        v1.0 - {brand_config['slogan']}<br>
        {brand_config['contact']}
    </p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass
