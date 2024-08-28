import os

import streamlit as st

from services import prompts
from helpers import util

st.set_page_config(
    page_title="Quick Chat",
    page_icon="💬",
    layout="wide"
)

import helpers.sidebar
import asyncio

helpers.sidebar.show()
openai_model = os.getenv('OPENAI_API_MODEL')
st.header("OpenAI Chat")
st.write(f"Get instant answers to your questions using OpenAI's ChatGPT ({openai_model}).")



# Ensure the session state is initialized
if "messages" not in st.session_state:
    initial_messages = [{"role": "system",
                         "content": prompts.quick_chat_system_prompt()}]
    st.session_state.messages = initial_messages

# Print all messages in the session state
for message in [m for m in st.session_state.messages if m["role"] != "system"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to the user prompt
if prompt := st.chat_input("Chat with OpenAI ChatGPT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    asyncio.run(util.chat(st.session_state.messages, prompt))
