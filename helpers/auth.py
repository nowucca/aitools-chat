from functools import wraps
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import uuid
from services.sessions import create_session, validate_session, delete_session

# Configuration for session management
SESSION_TIMEOUT_MINUTES = 30  # Total session expiry time
IDLE_TIMEOUT_MINUTES = 10  # Timeout due to inactivity

def _authenticate(username, password):
    """Check credentials from CSV and set up session if valid."""
    users_df = pd.read_csv('data/users.csv', dtype={"username":str, "password": str})
    user_row = users_df[(users_df['username'] == username) & (users_df['password'] == str(password))]
    if not user_row.empty:
        # Initialize session state for the authenticated user
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.session_state["session_key"] = str(uuid.uuid4())  # Unique session key
        st.session_state["session_start"] = datetime.now()  # Record session start time
        st.session_state["last_active"] = datetime.now()  # Record last activity time
        return True
    return False

import base64

def encode_credentials(username, password):
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return encoded_credentials

def login_page():
    """Display the login page for user authentication."""
    if is_authenticated():
        st.success(f"You are already logged in as {authenticated_user()}.")
        st.stop()

    st.title('Please login to access AI Tools Chat')
    st.write("<p/><p/>", unsafe_allow_html=True)
    st.markdown("<strong>Your username:</strong> is your Virginia Tech email without @vt.edu.", unsafe_allow_html=True)
    st.markdown("<strong>Your password:</strong> is the last 4 digits of your 9-digit student id number.",
                unsafe_allow_html=True)
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    st.write("<h6> ⚠️ If you reload the browser page, your session will be lost and you will need to login again.</h6>",
             unsafe_allow_html=True)

    if st.button("Submit"):
        if _authenticate(username, password):
            session_id, session_key = create_session(username)
            st.session_state["session_id"] = session_id
            st.session_state["session_key"] = session_key
            st.session_state["session_api_key"] = encode_credentials(username, password)
            st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("Incorrect Username or Password. Please try again.")

def authenticated_user():
    """Return the username of the authenticated user."""
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        return st.session_state.get("username", "Not logged in")
    return "Not logged in"

def is_authenticated():
    session_id = st.session_state.get("session_id")
    session_key = st.session_state.get("session_key")
    return validate_session(session_id, session_key)

def logout():
    """Logout the user and redirect to the login page."""
    session_id = st.session_state.get("session_id")
    if session_id:
        delete_session(session_id)
    st.session_state.clear()

    st.success("You have been logged out.")
    st.markdown('<meta http-equiv="refresh" content="1; URL=/Login">', unsafe_allow_html=True)

def require_authentication(func):
    """Decorator for requiring authentication."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            login_page()
            return  # Prevent access to the page until authenticated
        return func(*args, **kwargs)
    return wrapper
