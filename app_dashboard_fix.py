"""
Fixed version of dashboard stock summary section
"""
# Dalam bagian Dashboard, ganti kode stock summary dengan ini:

# Stock Summary
st.subheader("📊 Ringkasan Stok")
try:
    stock_summary = stock_management_service.get_stock_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_raw = sum(item[1] for item in stock_summary['raw_materials']) if stock_summary['raw_materials'] else 0
        st.metric("Bahan Mentah", f"{total_raw} pack")
    
    with col2:
        total_finished = sum(item[1] for item in stock_summary['finished_goods']) if stock_summary['finished_goods'] else 0
        st.metric("Barang Jadi", f"{total_finished} pcs")
    
    with col3:
        st.metric("Nilai Stok Bahan", format_currency(stock_summary['total_raw_value']))
    
    with col4:
        st.metric("Nilai Stok Jadi", format_currency(stock_summary['total_finished_value']))
        
except Exception as e:
    st.error(f"Error loading stock summary: {e}")
    # Fallback metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Bahan Mentah", "0 pack")
    with col2:
        st.metric("Barang Jadi", "0 pcs")
    with col3:
        st.metric("Nilai Stok Bahan", "Rp 0")
    with col4:
        st.metric("Nilai Stok Jadi", "Rp 0")
