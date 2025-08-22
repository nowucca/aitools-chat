import asyncio
import os
import uuid

import streamlit as st

import helpers.sidebar
from helpers import chat_helper
from helpers.auth import require_authentication, authenticated_user
from llm import prompts
from llm.llm import LLM_CHOICE


@require_authentication
def anthropic_chat():
    st.set_page_config(
        page_title="Anthropic Chat",
        page_icon="💬",
        layout="wide"
    )

    user = authenticated_user()
    helpers.sidebar.show()
    anthropic_model = os.getenv('ANTHROPIC_MODEL')
    st.header("Anthropic Chat")
    st.write(f"Get instant answers to your questions using Anthropic's Claude ({anthropic_model}).")

    anthropic_messages = "anthropic_messages"
    system_prompt_key = "anthropic_system_prompt"
    anthropic_api_key = "anthropic_api_key"

    conversation_assistant = chat_helper.ConversationHelper("anthropic_conversation_id")

    # Ensure the session state is initialized
    if anthropic_messages not in st.session_state:
        st.session_state[anthropic_messages] = []
    if system_prompt_key not in st.session_state:
        st.session_state[system_prompt_key] = prompts.quick_chat_system_prompt()

    # Layout row for system prompt and buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        api_key = st.text_input("Anthropic API Key", type="password", placeholder="your-anthropic-api-key", help="Enter your Anthropic API key.")
        expander_label = "System Prompt (Pre-Chat)" if not conversation_assistant.has_conversation_id() else "System Prompt (View Only)"
        with st.expander(expander_label, expanded=not conversation_assistant.has_conversation_id()):
            if not conversation_assistant.has_conversation_id():
                st.session_state[system_prompt_key] = st.text_area("Set a custom system prompt:",
                                                                   st.session_state[system_prompt_key])
            else:
                st.markdown(f"**{st.session_state[system_prompt_key]}**")

    with col2:
        if not conversation_assistant.has_conversation_id():
            if st.button("Begin Chat"):
                new_conversation_id = str(uuid.uuid4())
                st.session_state[anthropic_api_key] = api_key
                st.session_state[anthropic_messages] = [
                    {"role": "system", "content": st.session_state[system_prompt_key]}]
                conversation_assistant.set_conversation_id(new_conversation_id)
                st.rerun()
        else:
            if st.button("New Chat"):
                conversation_assistant.set_conversation_id(None)
                st.session_state[anthropic_api_key] = None
                st.session_state[anthropic_messages] = []
                st.session_state[system_prompt_key] = prompts.quick_chat_system_prompt()
                st.rerun()

    # Ensure conversation_id is in session state before showing chat input
    if not conversation_assistant.has_conversation_id():
        st.write("Please start a new chat to get a conversation ID.")
    else:
        # Display chat history
        for message in [m for m in st.session_state[anthropic_messages] if m["role"] != "system"]:
            with st.chat_message(message["role"]):
                st.markdown(f"""
                            <div class='st-chat-message'>
                                {message['content']}
                            </div>
                        """, unsafe_allow_html=True)

        # Show conversation ID
        st.markdown(
            f"<span style='font-size: 0.8em; color: gray'>Conversation: {conversation_assistant.get_conversation_id()}</span>",
            unsafe_allow_html=True)

        # Handle user input
        if prompt := st.chat_input("Chat with Anthropic Claude..."):
            st.session_state[anthropic_messages].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"""
                            <div class='st-chat-message'>
                                {prompt}
                            </div>
                        """, unsafe_allow_html=True)
            asyncio.run(chat_helper.chat(LLM_CHOICE.ANTHROPIC, 
                                         st.session_state[anthropic_api_key],
                                         st.session_state[anthropic_messages],
                                         conversation_assistant.get_conversation_id()))


anthropic_chat()
