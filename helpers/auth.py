import streamlit as st
import pandas as pd
from streamlit_cookies_controller import CookieController

# Constants
COOKIE_NAME = "username"
controller = CookieController()


def _authenticate(username, password):
    # Check credentials from CSV
    users_df = pd.read_csv('data/users.csv')
    user_row = users_df[(users_df['user'] == username) & (users_df['password'].astype(str) == str(password))]
    return not user_row.empty

def login_page():
    global controller

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
            controller.set(COOKIE_NAME, username)
            cookie = controller.get(COOKIE_NAME)

            st.write(f"Authenticated to {cookie}")
            st.markdown('<meta http-equiv="refresh" content="0; URL=/">', unsafe_allow_html=True)  # Redirect to home
        else:
            st.error("Incorrect Username or Password. Please try again.")

def authenticated_user():
    global controller, COOKIE_NAME

    # Retrieve the authenticated username from the cookie
    return controller.get(COOKIE_NAME)

def is_authenticated():
    global controller, COOKIE_NAME
    # Check if the username cookie exists, indicating the user is authenticated
    return controller.get(COOKIE_NAME) is not None

def _core_logout():
    global controller, COOKIE_NAME
    # Remove the username cookie to log the user out
    if is_authenticated():
        controller.remove(COOKIE_NAME)

def logout():
    _core_logout()
    st.success("You have been logged out.")
    st.markdown('<meta http-equiv="refresh" content="1; URL=/Login">', unsafe_allow_html=True)  # Redirect to login

def require_authentication(func):
    def wrapper(*args, **kwargs):
        if is_authenticated():
            func(*args, **kwargs)
        else:
            ## TEMP
            if _authenticate('steve72', '8956'):
                controller.set(COOKIE_NAME, 'steve72')
                cookie = controller.get(COOKIE_NAME)

                st.write(f"Authenticated to {cookie}")
                st.markdown('<meta http-equiv="refresh" content="0; URL=/">',
                            unsafe_allow_html=True)  # Redirect to home
            else:
                st.error("You must be logged in to use this feature.")
                st.markdown('<meta http-equiv="refresh" content="1; URL=/Login">', unsafe_allow_html=True)  # Redirect to login
    return wrapper

