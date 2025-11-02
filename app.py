import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
from PIL import Image
import io

# Import authentication
from auth import check_password

# Import services
from config.database import init_database
from config.brand_config import get_brand_config
from services.finance_service import FinanceService
from services.stock_service import StockService
from services.stock_management_service import StockManagementService
from services.initial_setup_service import InitialSetupService
from services.report_service import ReportService
from services.production_service import ProductionService
from services.sales_service import SalesService
from models.transaction import Transaction
from models.stock import StockItem
from utils.helpers import format_currency, safe_float

# Page configuration
st.set_page_config(
    page_title="VPants - Pembukuan & Stok Otomatis",
    page_icon="👙",
    layout="wide"
)

# Check authentication
if not check_password():
    st.stop()

# Initialize database and services
init_database()
finance_service = FinanceService()
stock_service = StockService()
stock_management_service = StockManagementService()
setup_service = InitialSetupService()
report_service = ReportService()
production_service = ProductionService()
sales_service = SalesService()

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

# Custom CSS
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
    .sale-item {{
        background: #f8f9fa;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        border-left: 3px solid {brand_config['primary_color']};
    }}
    .product-card {{
        background: linear-gradient(135deg, {brand_config['primary_color']}10, {brand_config['secondary_color']}10);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid {brand_config['primary_color']};
    }}
</style>
""", unsafe_allow_html=True)

# Display logo in sidebar
display_logo()

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Pilih Menu:",
    ["🏠 Dashboard", "💰 Input Manual", "📦 Stok", "🏭 Produksi", "📈 Laporan", "⚙️ Setup Awal"]
)

# Check setup status
setup_status = setup_service.get_setup_status()

# Show setup warning if not initialized
if not setup_status['finance_initialized'] and page != "⚙️ Setup Awal":
    st.warning("⚠️ Sistem belum diinisialisasi. Silakan buka **Setup Awal** terlebih dahulu.")
    if st.button("Pergi ke Setup Awal"):
        st.rerun()
    st.stop()

# Header
st.markdown(f'<div class="main-header">👙 {brand_config["name"]} - Sistem Pembukuan & Stok</div>', unsafe_allow_html=True)

# [REST OF YOUR ORIGINAL APP.PY CODE CONTINUES HERE...]
# Copy the rest of your original app.py content starting from Dashboard section

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
    
    try:
        stock_summary = stock_management_service.get_stock_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_raw = sum(item[1] for item in stock_summary['raw_materials']) if stock_summary['raw_materials'] else 0
            st.metric("Bahan Mentah", f"{total_raw} items")
        
        with col2:
            total_finished = sum(item[1] for item in stock_summary['finished_goods']) if stock_summary['finished_goods'] else 0
            st.metric("Barang Jadi", f"{total_finished} pcs")
        
        with col3:
            st.metric("Nilai Stok Bahan", format_currency(stock_summary['total_raw_value']))
        
        with col4:
            st.metric("Nilai Stok Jadi", format_currency(stock_summary['total_finished_value']))
            
    except Exception as e:
        st.error(f"Error loading stock summary: {e}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Bahan Mentah", "0 items")
        with col2:
            st.metric("Barang Jadi", "0 pcs")
        with col3:
            st.metric("Nilai Stok Bahan", "Rp 0")
        with col4:
            st.metric("Nilai Stok Jadi", "Rp 0")
    
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
        st.dataframe(df_recent.head(10), width='stretch')
    else:
        st.info("Belum ada transaksi dalam 7 hari terakhir.")

# [CONTINUE WITH THE REST OF YOUR ORIGINAL APP.PY...]
# Add all the other pages (Input Manual, Stok, Produksi, Laporan, Setup Awal)

