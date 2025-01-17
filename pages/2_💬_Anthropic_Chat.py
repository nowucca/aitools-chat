import asyncio
import os
import uuid

import streamlit as st

import helpers.sidebar
from helpers import chat_helper
from helpers.auth import require_authentication
from llm import prompts
from llm.llm import LLM_CHOICE


@require_authentication
def anthropic_chat():
    st.set_page_config(
        page_title="Quick Chat",
        page_icon="💬",
        layout="wide"
    )
    helpers.sidebar.show()
    anthropic_model = os.getenv('ANTHROPIC_MODEL')
    st.header("Anthropic Chat")
    st.write(f"Get instant answers to your questions using Anthropic's Claude ({anthropic_model}).")

    anthropic_messages = "anthropic_messages"
    conversation_assistant = chat_helper.ConversationHelper("anthropic_conversation_id")

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
    # Create tabs
    # Add "New Chat" button
    if st.button("New Chat"):
        # Generate a new conversation_id
        new_conversation_id = str(uuid.uuid4())
        # Clear the openai_messages in the session state
        st.session_state[anthropic_messages] = [{"role": "system",
                                              "content": prompts.quick_chat_system_prompt()}]
        # Store the new conversation_id in the session state
        conversation_assistant.set_conversation_id(new_conversation_id)
        st.rerun()

    # Ensure conversation_id is in session state before showing chat input
    if not conversation_assistant.has_conversation_id():
        st.write("Please start a new chat to get a conversation ID.")
    else:
        # Print all messages in the session state
        for message in [m for m in st.session_state[anthropic_messages] if m["role"] != "system"]:
            with st.chat_message(message["role"]):
                st.markdown(f"""
                    <div class='st-chat-message'>
                        {message['content']}
                    </div>
                """, unsafe_allow_html=True)

        # React to the user prompt
        st.markdown(f"<span style='font-size: 0.8em; color: gray'>Conversation: {conversation_assistant.get_conversation_id()}</span>", unsafe_allow_html=True)
        if prompt := st.chat_input("Chat with Anthropic Claude..."):
            st.session_state[anthropic_messages].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"""
                    <div class='st-chat-message'>
                        {prompt}
                    </div>
                """, unsafe_allow_html=True)
            asyncio.run(chat_helper.chat(LLM_CHOICE.ANTHROPIC, st.session_state["session_api_key"], st.session_state[anthropic_messages], conversation_assistant.get_conversation_id()))

anthropic_chat()
