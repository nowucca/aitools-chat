from helpers.auth import is_authenticated, authenticated_user, _authenticate
import streamlit as st
from helpers import sidebar
sidebar.show()

print("Login Page")
if is_authenticated():
    st.success(f"You are already logged in as {authenticated_user()}.")
    st.markdown(f"Go to the [OpenAI Chat](/OpenAI_Chat) page.")
    st.stop() # Exit early

print("Not authenticated")
st.title('Login to AI Tools Chat')
username = st.text_input("Enter Username")
password = st.text_input("Enter Password", type="password")

if st.button("Submit"):
    if _authenticate(username, password):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.success(f"You are now logged in as {authenticated_user()}.")
        st.markdown(f"Go to the [OpenAI Chat](/OpenAI_Chat) page.")
          # Exit early
    else:
        st.error("Incorrect Username or Password. Please try again.")
