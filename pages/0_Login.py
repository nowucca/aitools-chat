from helpers.auth import is_authenticated, authenticated_user, _authenticate
import streamlit as st
from helpers import sidebar
sidebar.show()

print("Login Page")
if is_authenticated():
    st.success(f"You are already logged in as {authenticated_user()}.")
    st.write("<p/>Navigate to other pages using the navigation links in the sidebar.<p/>", unsafe_allow_html=True)
    st.stop() # Exit early

print("Not authenticated")
st.title('Please login to access AI Tools Chat')
st.write("<p/><p/>", unsafe_allow_html=True)
st.markdown("<strong>Your username:</strong> is your Virginia Tech email without @vt.edu.", unsafe_allow_html=True)
st.markdown("<strong>Your password:</strong> is the last 4 digits of your 9-digit student id number.", unsafe_allow_html=True)
username = st.text_input("Enter Username")
password = st.text_input("Enter Password", type="password")

st.write("<h6> ⚠️ If you reload the browser page, your session will be lost and you will need to login again.</h6>", unsafe_allow_html=True)

if st.button("Submit"):
    if _authenticate(username, password):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.success(f"You are now logged in as {authenticated_user()}.")
        st.write("<p/>Navigate to other pages using the navigation links in the sidebar.<p/>", unsafe_allow_html=True)
          # Exit early
    else:
        st.error("Incorrect Username or Password. Please try again.")
