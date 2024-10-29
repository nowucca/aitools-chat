from helpers.auth import is_authenticated, authenticated_user, _authenticate, login_page
import streamlit as st
from helpers import sidebar
from helpers.auth import login_page

def login_page_bridge():
    st.set_page_config(
        page_title="Login",
        page_icon="🔒",
        layout="wide"
    )
    sidebar.show()
    login_page()

login_page_bridge()
