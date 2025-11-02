"""
Authentication system for VPants dengan multiple tokens
"""
import streamlit as st
import time

def check_password():
    """Returns `True` if the user had a valid token."""

    def token_entered():
        """Checks whether a token entered by the user is valid."""
        entered_token = st.session_state["token_input"]
        
        # Check against main token
        if entered_token == st.secrets["ACCESS_TOKEN"]:
            st.session_state["authenticated"] = True
            st.session_state["user_role"] = "admin"
            st.session_state["login_time"] = time.time()
            del st.session_state["token_input"]
            return
        
        # Check against team tokens
        if "team_tokens" in st.secrets:
            for role, token in st.secrets.team_tokens.items():
                if entered_token == token:
                    st.session_state["authenticated"] = True
                    st.session_state["user_role"] = role
                    st.session_state["login_time"] = time.time()
                    del st.session_state["token_input"]
                    return
        
        st.session_state["authenticated"] = False

    # Return True if already authenticated
    if st.session_state.get("authenticated", False):
        # Check if session is expired (12 hours)
        if time.time() - st.session_state.get("login_time", 0) > 43200:
            st.session_state["authenticated"] = False
        else:
            return True

    # Show token input
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>👙 VPants System</h1>
        <p style="color: #666;">SMART WOMEN - Management System</p>
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; margin: 1rem 0;">
            <h3 style="color: white; margin: 0;">🔐 Secure Access</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input(
            "Access Token",
            type="password",
            on_change=token_entered,
            key="token_input",
            placeholder="Masukkan token akses tim"
        )
        
        if "authenticated" in st.session_state:
            if not st.session_state["authenticated"]:
                st.error("❌ Token tidak valid")
        
        st.info("""
        **Untuk token akses, hubungi:**  
        📞 Admin: 085157149669  
        👥 Token berbeda untuk setiap role:
        - Admin (Full access)
        - Manager (Laporan & Monitoring) 
        - Staff (Input transaksi)
        - Warehouse (Stok & Produksi)
        - Sales (Penjualan saja)
        """)
        
        # Logout button for when authenticated
        if st.session_state.get("authenticated", False):
            if st.button("🚪 Logout"):
                for key in ["authenticated", "user_role", "login_time"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    return False
