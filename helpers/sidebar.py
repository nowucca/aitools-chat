import streamlit as st
from helpers.auth import is_authenticated, logout, authenticated_user

from helpers.auth import login_page

def show() -> None:
    with st.sidebar:
        st.markdown(f"""
            <a href="/" style="color:black;text-decoration: none;">
                <div style="display:table;margin-top:-16rem;margin-left:0%;">
                    <span style="color: black">&nbsp;AI Tools Chat</span>
                    <span style="font-size: 0.8em; color: grey">&nbsp;&nbsp;v0.1.1</span>
                </div>
            </a>

                """, unsafe_allow_html=True)
        login_text = '🔒' if is_authenticated() else '🔓'
        login_user = f'Logged in as {authenticated_user()}' if is_authenticated() else 'Not logged in'
        st.markdown(f"""
            <div style="display:table;margin-top:1rem;margin-bottom:1rem">
                <span>{login_text}&nbsp;{login_user}</span>
            </div>
        """, unsafe_allow_html=True)
        if is_authenticated():
            logout_button = st.button("🚪 Logout")
            if logout_button:
                logout()
                st.session_state.clear()
                st.rerun()
        else:
            login_button = st.button("🔑 Login")
            if login_button:
                st.markdown('<meta http-equiv="refresh" content="0; URL=/Login">', unsafe_allow_html=True)
