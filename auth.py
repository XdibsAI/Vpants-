"""
Authentication system for VPants
"""
import streamlit as st
import time
import hashlib

def check_password():
    """Returns `True` if the user had a valid token."""
    
    # Initialize session state variables
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "login_time" not in st.session_state:
        st.session_state.login_time = 0

    def token_entered():
        """Checks whether a token entered by the user is valid."""
        entered_token = st.session_state.get("token_input", "")
        
        if not entered_token:
            st.session_state.authenticated = False
            return
        
        # Define valid tokens (hardcoded for now since secrets might not be loading)
        valid_tokens = {
            "vpants-admin-2024": "admin",
            "vpants-manager-2024": "manager", 
            "vpants-staff-2024": "staff",
            "vpants-gudang-2024": "warehouse",
            "vpants-sales-2024": "sales"
        }
        
        # Check if token is valid
        if entered_token in valid_tokens:
            st.session_state.authenticated = True
            st.session_state.user_role = valid_tokens[entered_token]
            st.session_state.login_time = time.time()
            st.session_state.token_input = ""  # Clear the input
            st.rerun()
        else:
            st.session_state.authenticated = False
            st.error("❌ Token tidak valid")

    # Return True if already authenticated and session not expired
    if st.session_state.authenticated:
        # Check if session is expired (12 hours)
        if time.time() - st.session_state.login_time > 43200:  # 12 hours in seconds
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.info("🔒 Session telah expired, silakan login kembali")
        else:
            return True

    # Show login interface
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>👙 VPants System</h1>
        <p style="color: #666; font-size: 1.2rem;">SMART WOMEN - Management System</p>
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; margin: 2rem 0;">
            <h3 style="color: white; margin: 0;">🔐 Secure Access Required</h3>
            <p style="color: white; opacity: 0.9;">Masukkan token akses untuk melanjutkan</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "Access Token",
            type="password",
            key="token_input",
            placeholder="Masukkan token akses tim",
            label_visibility="collapsed"
        )
        
        # Login button
        if st.button("🚀 Login", use_container_width=True):
            token_entered()
        
        # Error message
        if "authenticated" in st.session_state and not st.session_state.authenticated:
            st.error("❌ Token tidak valid. Silakan coba lagi.")
        
        # Information box
        with st.expander("ℹ️ Informasi Token"):
            st.info("""
            **Token Akses Tim:**
            - Admin: `vpants-admin-2024`
            - Manager: `vpants-manager-2024`
            - Staff: `vpants-staff-2024` 
            - Gudang: `vpants-gudang-2024`
            - Sales: `vpants-sales-2024`
            
            **Hubungi admin untuk token baru:**
            📞 085157149669
            """)

    return False

def get_current_user():
    """Get current user role"""
    return st.session_state.get("user_role", "unknown")

def is_admin():
    """Check if current user is admin"""
    return get_current_user() == "admin"

def logout():
    """Logout current user"""
    for key in ["authenticated", "user_role", "login_time"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
