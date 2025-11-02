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

# Initialize database
init_database()

# Initialize services
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

# Input Manual Page
elif page == "💰 Input Manual":
    st.header("💰 Input Transaksi Manual")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛒 Penjualan", "📦 Pack Sales", "🏭 Produksi", "🛍️ Belanja Bahan", "💸 Lainnya"])
    
    with tab1:
        st.subheader("🛒 Penjualan Retail")
        
        # Dynamic form untuk multiple items - di luar form utama
        if 'sale_items' not in st.session_state:
            st.session_state.sale_items = [{'product': 'Celana Dalam VPants', 'size': 'M', 'quantity': 1}]
        
        # Controls untuk manage items (di luar form)
        col_controls, _ = st.columns([2, 1])
        with col_controls:
            if st.button("➕ Tambah Item", key="add_item_btn"):
                st.session_state.sale_items.append({'product': 'Celana Dalam VPants', 'size': 'M', 'quantity': 1})
                st.rerun()
        
        # Tampilkan items saat ini
        st.write("**Item yang Dijual:**")
        for i, item in enumerate(st.session_state.sale_items):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                product = st.selectbox(
                    f"Produk {i+1}",
                    ['Celana Dalam VPants', 'Celana Pembalut VPants', 'Celana Dalam Premium'],
                    index=0 if item['product'] == 'Celana Dalam VPants' else 1 if item['product'] == 'Celana Pembalut VPants' else 2,
                    key=f"product_{i}"
                )
            with col2:
                size = st.selectbox(
                    f"Ukuran {i+1}",
                    ['S', 'M', 'L', 'XL', 'XXL'],
                    index=['S', 'M', 'L', 'XL', 'XXL'].index(item['size']),
                    key=f"size_{i}"
                )
            with col3:
                quantity = st.number_input(
                    f"Qty {i+1}",
                    min_value=1,
                    value=item['quantity'],
                    key=f"qty_{i}"
                )
            with col4:
                if i > 0:
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.sale_items.pop(i)
                        st.rerun()
            
            # Update session state
            st.session_state.sale_items[i] = {'product': product, 'size': size, 'quantity': quantity}
        
        # Bonus items untuk pembelian banyak
        total_qty = sum(item['quantity'] for item in st.session_state.sale_items)
        if total_qty >= 5:
            st.success(f"🎉 Pembelian {total_qty} pcs dapat bonus!")
            bonus_item = st.checkbox("Tambahkan bonus 1 pcs (size M)", key="bonus_checkbox")
        else:
            bonus_item = False
        
        # Form untuk input transaksi
        with st.form("retail_sale_form"):
            col1, col2 = st.columns(2)
            with col1:
                discount = st.number_input("Diskon (%)", min_value=0, max_value=100, value=0, key="discount_input")
                payment_method = st.selectbox("Metode Bayar", ["Cash", "Transfer", "Shopee", "Tokopedia"], key="payment_method")
            with col2:
                customer_notes = st.text_input("Catatan Pelanggan", key="customer_notes")
                admin_fee = st.number_input("Biaya Admin", min_value=0, value=0, key="admin_fee")
            
            # Calculate total (harga berbeda untuk tipe produk)
            price_per_piece = 75000  # Harga default untuk celana dalam biasa
            if any('Pembalut' in item['product'] for item in st.session_state.sale_items):
                price_per_piece = 85000  # Harga untuk celana pembalut
            elif any('Premium' in item['product'] for item in st.session_state.sale_items):
                price_per_piece = 95000  # Harga untuk premium
            
            estimated_total = total_qty * price_per_piece
            final_total = estimated_total * (1 - discount/100) - admin_fee
            
            st.info(f"**Total Estimasi:** {format_currency(estimated_total)} | "
                   f"**Setelah Diskon {discount}%:** {format_currency(estimated_total * (1 - discount/100))} | "
                   f"**Final:** {format_currency(final_total)}")
            
            submitted = st.form_submit_button("💾 Simpan Penjualan")
            
            if submitted:
                try:
                    # Process each sale item
                    for item in st.session_state.sale_items:
                        transaction = Transaction(
                            type='sale',
                            category='retail_sale',
                            amount=final_total / len(st.session_state.sale_items),  # Split amount
                            quantity=item['quantity'],
                            size=item['size'],
                            notes=f"Penjualan {item['product']} {item['size']} - {customer_notes}"
                        )
                        
                        # Update balance
                        finance_service.update_balance(transaction)
                        
                        # Update stock
                        stock_item = StockItem(
                            item_type='finished',
                            item_name=item['product'],
                            quantity=-item['quantity'],
                            size=item['size']
                        )
                        stock_service.update_stock(stock_item)
                    
                    # Add bonus item if applicable
                    if total_qty >= 5 and bonus_item:
                        bonus_transaction = Transaction(
                            type='sale',
                            category='bonus',
                            amount=0,
                            quantity=1,
                            size='M',
                            notes="Bonus untuk pembelian 5+ pcs"
                        )
                        finance_service.update_balance(bonus_transaction)
                        
                        bonus_stock = StockItem(
                            item_type='finished',
                            item_name='Celana Dalam VPants',
                            quantity=-1,
                            size='M'
                        )
                        stock_service.update_stock(bonus_stock)
                    
                    st.success(f"✅ Penjualan {total_qty} pcs berhasil dicatat!")
                    st.session_state.sale_items = [{'product': 'Celana Dalam VPants', 'size': 'M', 'quantity': 1}]
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.subheader("📦 Pack Sales")
        
        with st.form("pack_sale_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                pack_type = st.selectbox(
                    "Jenis Pack",
                    ["Pack 3 pcs", "Pack 5 pcs", "Pack 10 pcs", "Custom Pack"]
                )
                
                if pack_type == "Pack 3 pcs":
                    pack_price = 200000  # 3 x 75000 = 225000, diskon jadi 200000
                    pack_qty = 3
                elif pack_type == "Pack 5 pcs":
                    pack_price = 300000  # 5 x 75000 = 375000, diskon jadi 300000
                    pack_qty = 5
                elif pack_type == "Pack 10 pcs":
                    pack_price = 550000  # 10 x 75000 = 750000, diskon jadi 550000
                    pack_qty = 10
                else:
                    pack_qty = st.number_input("Jumlah pcs dalam pack", min_value=2, value=3)
                    pack_price = st.number_input("Harga Pack", min_value=0, value=75000 * pack_qty)
                
                st.write(f"**Harga per pcs:** {format_currency(pack_price / pack_qty)}")
            
            with col2:
                st.write("**Komposisi Pack:**")
                sizes = ['S', 'M', 'L', 'XL', 'XXL']
                size_distribution = {}
                
                for size in sizes:
                    size_distribution[size] = st.number_input(
                        f"Qty Size {size}",
                        min_value=0,
                        max_value=pack_qty,
                        value=0,
                        key=f"pack_{size}"
                    )
                
                total_distributed = sum(size_distribution.values())
                if total_distributed != pack_qty:
                    st.warning(f"Total distribusi: {total_distributed} pcs (harus {pack_qty} pcs)")
            
            customer_notes = st.text_input("Catatan Pack")
            discount = st.number_input("Diskon Pack (%)", min_value=0, max_value=100, value=0)
            
            final_pack_price = pack_price * (1 - discount/100)
            st.info(f"**Harga Pack:** {format_currency(pack_price)} → **Final:** {format_currency(final_pack_price)}")
            
            submitted = st.form_submit_button("💾 Simpan Pack Sale")
            
            if submitted:
                if total_distributed != pack_qty:
                    st.error(f"Total distribusi size harus {pack_qty} pcs!")
                else:
                    try:
                        # Record pack sale transaction
                        transaction = Transaction(
                            type='sale',
                            category='pack_sale',
                            amount=final_pack_price,
                            quantity=pack_qty,
                            size='MIXED',
                            notes=f"Pack {pack_type} - {customer_notes}"
                        )
                        
                        new_balance = finance_service.update_balance(transaction)
                        
                        # Update stock for each size
                        for size, qty in size_distribution.items():
                            if qty > 0:
                                stock_item = StockItem(
                                    item_type='finished',
                                    item_name='Celana Dalam VPants',
                                    quantity=-qty,
                                    size=size
                                )
                                stock_service.update_stock(stock_item)
                        
                        st.success(f"✅ Pack {pack_type} ({pack_qty} pcs) berhasil dijual!")
                        st.success(f"💰 Saldo baru: {format_currency(new_balance)}")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("🏭 Input Produksi")
        
        with st.form("production_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.selectbox(
                    "Produk yang Diproduksi",
                    ['Celana Dalam VPants', 'Celana Pembalut VPants', 'Celana Dalam Premium']
                )
                size = st.selectbox("Ukuran", ['S', 'M', 'L', 'XL', 'XXL'])
                quantity = st.number_input("Jumlah Produksi", min_value=1, value=10)
                labor_cost = st.number_input("Ongkos Jahit Total", min_value=0, value=120000)
            
            with col2:
                st.write("**Bahan yang Digunakan:**")
                
                # Get available materials
                materials = production_service.get_raw_materials()
                materials_used = []
                
                for material in materials:
                    material_id, name, unit, cost = material
                    qty_used = st.number_input(
                        f"{name} ({unit})",
                        min_value=0.0,
                        value=0.0,
                        step=0.1,
                        key=f"mat_{material_id}"
                    )
                    if qty_used > 0:
                        materials_used.append({
                            'material_id': material_id,
                            'quantity': qty_used,
                            'name': name,
                            'unit': unit
                        })
            
            production_notes = st.text_input("Catatan Produksi")
            
            # Calculate estimated cost
            materials_cost = sum(mat['quantity'] * next((m[3] for m in materials if m[0] == mat['material_id']), 0) 
                               for mat in materials_used)
            total_cost = labor_cost + materials_cost
            
            st.info(f"**Estimasi Biaya:** Bahan {format_currency(materials_cost)} + "
                   f"Ongkos {format_currency(labor_cost)} = {format_currency(total_cost)}")
            
            submitted = st.form_submit_button("🏭 Simpan Produksi")
            
            if submitted:
                try:
                    # Record production
                    production_service.record_production(
                        product_name=product_name,
                        size=size,
                        quantity=quantity,
                        labor_cost=labor_cost,
                        materials_used=materials_used,
                        notes=production_notes
                    )
                    
                    st.success(f"✅ Produksi {quantity} pcs {product_name} {size} berhasil dicatat!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab4:
        st.subheader("🛍️ Belanja Bahan Mentah")
        
        with st.form("material_purchase_form"):
            materials = production_service.get_raw_materials()
            
            col1, col2, col3 = st.columns(3)
            
            purchased_items = []
            for i, material in enumerate(materials):
                material_id, name, unit, cost = material
                
                if i % 3 == 0:
                    current_col = col1
                elif i % 3 == 1:
                    current_col = col2
                else:
                    current_col = col3
                
                with current_col:
                    st.write(f"**{name}**")
                    purchase_qty = st.number_input(
                        f"Qty ({unit})",
                        min_value=0.0,
                        value=0.0,
                        step=0.1,
                        key=f"purchase_{material_id}"
                    )
                    purchase_price = st.number_input(
                        f"Harga Total",
                        min_value=0,
                        value=0,
                        key=f"price_{material_id}"
                    )
                    
                    if purchase_qty > 0:
                        purchased_items.append({
                            'material_id': material_id,
                            'name': name,
                            'quantity': purchase_qty,
                            'unit': unit,
                            'price': purchase_price
                        })
            
            purchase_notes = st.text_input("Catatan Pembelian")
            total_purchase = sum(item['price'] for item in purchased_items)
            
            st.info(f"**Total Pembelian:** {format_currency(total_purchase)}")
            
            submitted = st.form_submit_button("🛍️ Simpan Pembelian")
            
            if submitted:
                if not purchased_items:
                    st.error("Pilih minimal 1 bahan yang dibeli!")
                else:
                    try:
                        for item in purchased_items:
                            # Record transaction
                            transaction = Transaction(
                                type='purchase',
                                category='material_purchase',
                                amount=item['price'],
                                quantity=item['quantity'],
                                unit=item['unit'],
                                notes=f"Beli {item['name']} - {purchase_notes}"
                            )
                            
                            finance_service.update_balance(transaction)
                            
                            # Update stock
                            stock_item = StockItem(
                                item_type='material',
                                item_name=item['name'],
                                quantity=item['quantity'],
                                unit=item['unit']
                            )
                            stock_service.update_stock(stock_item)
                        
                        st.success(f"✅ Pembelian {len(purchased_items)} bahan berhasil dicatat!")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab5:
        st.subheader("💸 Transaksi Lainnya")
        
        transaction_type = st.selectbox(
            "Jenis Transaksi:",
            ["Pemasukan Shopee", "Penarikan Tunai", "Biaya Admin", "Biaya Lain"]
        )
        
        with st.form("other_transaction_form"):
            if transaction_type == "Pemasukan Shopee":
                amount = st.number_input("Jumlah Pemasukan Bersih (Rp)", min_value=0, step=1000)
                notes = st.text_input("Catatan (opsional)")
                
            elif transaction_type == "Penarikan Tunai":
                amount = st.number_input("Jumlah Penarikan (Rp)", min_value=0, step=1000)
                st.info(f"Biaya admin: Rp 3,000 | Total dikurangi: {format_currency(amount + 3000)}")
                notes = st.text_input("Alasan penarikan (opsional)")
                
            else:  # Biaya Admin/Lain
                category = st.selectbox("Jenis Biaya", ["Biaya Admin", "Biaya ATM", "Transportasi", "Lainnya"])
                amount = st.number_input("Jumlah Pengeluaran (Rp)", min_value=0, step=1000)
                notes = st.text_input("Keterangan biaya")
            
            submitted = st.form_submit_button("💾 Simpan Transaksi")
            
            if submitted:
                if amount <= 0:
                    st.error("Jumlah transaksi harus lebih dari 0")
                else:
                    # Map transaction types
                    type_mapping = {
                        "Pemasukan Shopee": "se_income", 
                        "Penarikan Tunai": "withdrawal",
                        "Biaya Admin": "expense",
                        "Biaya Lain": "expense"
                    }
                    
                    transaction_category = transaction_type.replace(" ", "_")
                    
                    transaction = Transaction(
                        type=type_mapping[transaction_type],
                        category=transaction_category,
                        amount=amount,
                        notes=notes
                    )
                    
                    try:
                        new_balance = finance_service.update_balance(transaction)
                        st.success(f"✅ Transaksi berhasil disimpan! Saldo baru: {format_currency(new_balance)}")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Stock Page
elif page == "📦 Stok":
    st.header("📊 Management Stok")
    
    tab1, tab2, tab3 = st.tabs(["Lihat Stok", "Update Stok Manual", "Riwayat Stock"])
    
    with tab1:
        st.subheader("Level Stok Saat Ini")
        
        stock_summary = stock_management_service.get_stock_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📦 Bahan Mentah & Material**")
            if stock_summary['raw_materials']:
                df_raw = pd.DataFrame(stock_summary['raw_materials'], columns=['Bahan', 'Quantity'])
                st.dataframe(df_raw, width='stretch')
            else:
                st.info("Belum ada stok bahan mentah")
        
        with col2:
            st.write("**👙 Barang Jadi (per Ukuran)**")
            if stock_summary['finished_goods']:
                df_finished = pd.DataFrame(stock_summary['finished_goods'], columns=['Ukuran', 'Quantity'])
                st.dataframe(df_finished, width='stretch')
            else:
                st.info("Belum ada stok barang jadi")
        
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
                item_type = st.selectbox("Jenis Item", ["Bahan Mentah", "Barang Jadi", "Material"])
                item_name = st.text_input("Nama Item")
            with col2:
                if item_type == "Barang Jadi":
                    size = st.selectbox("Ukuran", ["S", 'M', 'L', 'XL', 'XXL'])
                else:
                    size = None
                quantity = st.number_input("Quantity (+/- untuk tambah/kurang)", step=1)
            
            notes = st.text_input("Alasan update (opsional)")
            
            submitted = st.form_submit_button("pdate Stok")
            
            if submitted:
                try:
                    stock_type = "raw" if item_type == "Bahan Mentah" else "finished" if item_type == "Barang Jadi" else "material"
                    
                    stock_management_service.adjust_stock(
                        item_type=stock_type,
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
            st.dataframe(df_history, width='stretch')
        else:
            st.info("Belum ada perubahan stok dalam periode ini")

# Produksi Page
elif page == "🏭 Produksi":
    st.header("🏭 Manajemen Produksi")
    
    tab1, tab2 = st.tabs(["Riwayat Produksi", "Bahan Mentah"])
    
    with tab1:
        st.subheader("📋 Riwayat Produksi")
        
        production_history = production_service.get_production_history(30)
        
        if production_history:
            df_production = pd.DataFrame(production_history, 
                                       columns=['Produk', 'Size', 'Qty', 'Ongkos', 'Bahan', 'Total', 'Notes', 'Tanggal'])
            df_production['Ongkos'] = df_production['Ongkos'].apply(format_currency)
            df_production['Bahan'] = df_production['Bahan'].apply(format_currency)
            df_production['Total'] = df_production['Total'].apply(format_currency)
            
            st.dataframe(df_production, width='stretch')
            
            # Production summary
            total_produced = df_production['Qty'].sum()
            total_cost = df_production['Total'].astype(str).str.replace('Rp ', '').str.replace('.', '').astype(float).sum()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Produksi (30 hari)", f"{total_produced} pcs")
            with col2:
                st.metric("Total Biaya Produksi", format_currency(total_cost))
        else:
            st.info("Belum ada data produksi dalam 30 hari terakhir")
    
    with tab2:
        st.subheader("📦 Bahan Mentah Tersedia")
        
        materials = production_service.get_raw_materials()
        
        if materials:
            df_materials = pd.DataFrame(materials, columns=['ID', 'Nama', 'Unit', 'Harga/Unit'])
            df_materials['Harga/Unit'] = df_materials['Harga/Unit'].apply(format_currency)
            
            st.dataframe(df_materials, width='stretch')
        else:
            st.info("Tidak ada data bahan mentah")

# Laporan Page
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
                st.dataframe(df_monthly, width='stretch')
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
            
            st.dataframe(filtered_df, width='stretch')
            
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

# Setup Awal Page - FIXED
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
    
    with col3:  # FIXED: ini col3, bukan tab3
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
        v2.0 - {brand_config['slogan']}<br>
        {brand_config['contact']}
    </p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass
