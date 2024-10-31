import os
import uuid
import asyncio
from typing import List, Dict

import streamlit as st

from helpers.auth import require_authentication, authenticated_user
from llm import prompts
from helpers import chat_helper
from llm.llm import LLM_CHOICE
import helpers.sidebar



@require_authentication
def openai_chat():
    st.set_page_config(
        page_title="Open AI Chat",
        page_icon="💬",
        layout="wide"
    )

    user = authenticated_user()

    helpers.sidebar.show()

    conversation_assistant = chat_helper.ConversationHelper("openai_conversation_id")

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


    # Add "New Chat" button
    if st.button("New Chat"):
        # Generate a new conversation_id
        new_conversation_id = str(uuid.uuid4())
        # Clear the openai_messages in the session state
        st.session_state[openai_messages] = [{"role": "system",
                                              "content": prompts.quick_chat_system_prompt()}]
        # Store the new conversation_id in the session state
        conversation_assistant.set_conversation_id(new_conversation_id)
        st.rerun()

    # Ensure conversation_id is in session state before showing chat input
    if not conversation_assistant.has_conversation_id():
        st.write("Please start a new chat to get a conversation ID.")
    else:
        # Print all messages in the session state
        for message in [m for m in st.session_state[openai_messages] if m["role"] != "system"]:
            with st.chat_message(message["role"]):
                st.markdown(f"""
                            <div class='st-chat-message'>
                                {message['content']}
                            </div>
                        """, unsafe_allow_html=True)

        # React to the user prompt
        st.markdown(f"<span style='font-size: 0.8em; color: gray'>Conversation: {conversation_assistant.get_conversation_id()}</span>", unsafe_allow_html=True)
        if prompt := st.chat_input("Chat with OpenAI ChatGPT..."):
            st.session_state[openai_messages].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"""
                            <div class='st-chat-message'>
                                {prompt}
                            </div>
                        """, unsafe_allow_html=True)
            asyncio.run(chat_helper.chat(LLM_CHOICE.OPENAI, st.session_state[openai_messages], conversation_assistant.get_conversation_id()))

openai_chat()
