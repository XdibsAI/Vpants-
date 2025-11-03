import streamlit as st

def check_password():
    """Returns `True` if the user had the correct access token."""
    
    def token_entered():
        """Checks whether a token entered by the user is correct."""
        if "token" in st.session_state and st.session_state.token == st.secrets.get("ACCESS_TOKEN", ""):
            st.session_state.password_correct = True
        else:
            st.session_state.password_correct = False

    # Return True if already authenticated
    if st.session_state.get("password_correct", False):
        return True

    # Show token input
    st.text_input(
        "Enter access token", 
        type="password", 
        on_change=token_entered, 
        key="token",
        label_visibility="visible"
    )

    # Show error if token is incorrect
    if "password_correct" in st.session_state and not st.session_state.password_correct:
        st.error("😕 Token incorrect")
        return False
    
    return False
