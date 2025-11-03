import streamlit as st
import os

st.set_page_config(
    page_title="VPants System", 
    page_icon="👙",
    layout="wide"
)

# Simple authentication
def check_auth():
    if st.session_state.get("authenticated"):
        return True
    
    st.title("👙 VPants System")
    st.subheader("SMART WOMEN - Management System") 
    st.write("🔐 Secure Access Required")
    
    token = st.text_input("Masukkan token akses untuk melanjutkan", type="password")
    
    if st.button("Login"):
        correct_token = os.environ.get("ACCESS_TOKEN", st.secrets.get("ACCESS_TOKEN", "default-token"))
        if token == correct_token:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Token salah! Silakan coba lagi.")
    
    return False

# Check auth
if not check_auth():
    st.stop()

# Main app
st.title("👙 VPants System")
st.subheader("SMART WOMEN - Management System")
st.success("✅ Authentication successful! Welcome to VPants System.")
st.info("Aplikasi berhasil diakses!")
