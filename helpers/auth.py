import streamlit as st
import pandas as pd

def _authenticate(username, password):
    users_df = pd.read_csv('data/users.csv')
    user_row = users_df[(users_df['user'] == username) & (users_df['password'].astype(str) == str(password))]
    return not user_row.empty

def login_page():
    print("Login Page")
    if is_authenticated():
        st.success(f"You are already logged in as {authenticated_user()}.")
        return # Exit early

    print("Not authenticated")
    st.title('Login to AI Tools Chat')
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    if st.button("Submit"):
        if _authenticate(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            print("Authenticated")
        else:
            st.error("Incorrect Username or Password. Please try again.")

def authenticated_user():
    return st.session_state.username

def is_authenticated():
    return hasattr(st.session_state, "authenticated") and st.session_state.authenticated

def _core_logout():
    st.session_state.authenticated = False
    st.session_state.username = None

def logout():
    _core_logout()
    st.success("You have been logged out.")

def require_authentication(func):
    def wrapper(*args, **kwargs):
        if is_authenticated():
            func(*args, **kwargs)
        else:
            _core_logout()
            st.error("You must be logged in to use this feature.")
            st.markdown('<meta http-equiv="refresh" content="1; URL=/Login">', unsafe_allow_html=True)  # Redirect to the login page after 1 second
    return wrapper
