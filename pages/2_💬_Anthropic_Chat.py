import os
import streamlit as st
from llm import prompts
from helpers import chat_helper
from llm.llm import LLM_CHOICE

st.set_page_config(
    page_title="Quick Chat",
    page_icon="💬",
    layout="wide"
)

import helpers.sidebar
import asyncio

helpers.sidebar.show()
anthropic_model = os.getenv('ANTHROPIC_MODEL')
st.header("Anthropic Chat")
st.write(f"Get instant answers to your questions using Anthropic's Claude ({anthropic_model}).")

anthropic_messages = "anthropic_messages"

# Ensure the session state is initialized
if anthropic_messages not in st.session_state:
    initial_messages = [{"role": "system",
                         "content": prompts.quick_chat_system_prompt()}]
    st.session_state[anthropic_messages] = initial_messages

# Add custom CSS to control the width of the chat content
st.markdown(
    """
    <style>
    .st-chat-message {
        max-width: 700px !important;
        word-wrap: break-word !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Print all messages in the session state
for message in [m for m in st.session_state[anthropic_messages] if m["role"] != "system"]:
    with st.chat_message(message["role"]):
        st.markdown(f"""
            <div class='st-chat-message'>
                {message['content']}
            </div>
        """, unsafe_allow_html=True)

# React to the user prompt
if prompt := st.chat_input("Chat with Anthropic Claude..."):
    st.session_state[anthropic_messages].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"""
            <div class='st-chat-message'>
                {prompt}
            </div>
        """, unsafe_allow_html=True)
    asyncio.run(chat_helper.chat(LLM_CHOICE.ANTHROPIC, st.session_state[anthropic_messages]))
