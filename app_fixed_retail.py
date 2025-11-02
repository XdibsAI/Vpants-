# GANTI BAGIAN RETAIL SALES FORM DENGAN INI:

with tab1:
    st.subheader("🛒 Penjualan Retail")
    
    # Dynamic form untuk multiple items - di luar form utama
    if 'sale_items' not in st.session_state:
        st.session_state.sale_items = [{'product': 'Celana VPants Basic', 'size': 'M', 'quantity': 1}]
    
    # Controls untuk manage items (di luar form)
    col_controls, _ = st.columns([2, 1])
    with col_controls:
        if st.button("➕ Tambah Item", key="add_item_btn"):
            st.session_state.sale_items.append({'product': 'Celana VPants Basic', 'size': 'M', 'quantity': 1})
            st.experimental_rerun()
    
    # Tampilkan items saat ini
    st.write("**Item yang Dijual:**")
    for i, item in enumerate(st.session_state.sale_items):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            product = st.selectbox(
                f"Produk {i+1}",
                ['Celana VPants Basic', 'Celana VPants Premium'],
                index=0 if item['product'] == 'Celana VPants Basic' else 1,
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
                    st.experimental_rerun()
        
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
        
        # Calculate total
        estimated_total = total_qty * 150000  # Simplified calculation
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
                        item_name='Celana VPants Basic',
                        quantity=-1,
                        size='M'
                    )
                    stock_service.update_stock(bonus_stock)
                
                st.success(f"✅ Penjualan {total_qty} pcs berhasil dicatat!")
                st.session_state.sale_items = [{'product': 'Celana VPants Basic', 'size': 'M', 'quantity': 1}]
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
