import os

import streamlit as st

from llm import prompts
from helpers import chat_helper
from llm.llm import LLM_CHOICE

st.set_page_config(
    page_title="Open AI Chat",
    page_icon="💬",
    layout="wide"
)

import helpers.sidebar
import asyncio

helpers.sidebar.show()
openai_model = os.getenv('OPENAI_API_MODEL')
st.header("OpenAI Chat")
st.write(f"Get instant answers to your questions using OpenAI's ChatGPT ({openai_model}).")

openai_messages = "openai_messages"

# Ensure the session state is initialized
if openai_messages not in st.session_state:
    initial_messages = [{"role": "system",
                         "content": prompts.quick_chat_system_prompt()}]
    st.session_state[openai_messages] = initial_messages

# Add custom CSS to control the width of the chat content
st.markdown(
    """
    <style>
    .st-chat-message {
        max-width: 700px;
        word-wrap: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Print all messages in the session state
for message in [m for m in st.session_state[openai_messages] if m["role"] != "system"]:
    with st.chat_message(message["role"]):
        st.markdown(f"""
                    <div class='st-chat-message'>
                        {message['content']}
                    </div>
                """, unsafe_allow_html=True)


# React to the user prompt
if prompt := st.chat_input("Chat with OpenAI ChatGPT..."):
    st.session_state[openai_messages].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"""
                    <div class='st-chat-message'>
                        {prompt}
                    </div>
                """, unsafe_allow_html=True)
    asyncio.run(chat_helper.chat(LLM_CHOICE.OPENAI, st.session_state[openai_messages]))
