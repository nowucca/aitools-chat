import os
import uuid
import asyncio
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
    system_prompt_key = "system_prompt"

    # Ensure the session state is initialized
    if openai_messages not in st.session_state:
        st.session_state[openai_messages] = []
    if system_prompt_key not in st.session_state:
        st.session_state[system_prompt_key] = prompts.quick_chat_system_prompt()

    # Layout for expander and chat button in the same row
    col1, col2 = st.columns([0.75, 0.25])  # Adjust column ratios as needed

    with col1:
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
                st.session_state[openai_messages] = [{"role": "system", "content": st.session_state[system_prompt_key]}]
                conversation_assistant.set_conversation_id(new_conversation_id)
                st.rerun()
        else:
            if st.button("New Chat"):
                # Stop the conversation and remove it
                conversation_assistant.set_conversation_id(None)
                st.session_state[openai_messages] = []
                st.session_state[system_prompt_key] = prompts.quick_chat_system_prompt()
                st.rerun()

    # Ensure conversation_id is in session state before showing chat input
    if not conversation_assistant.has_conversation_id():
        st.write("Please start a new chat to get a conversation ID.")
    else:
        # Display chat history
        for message in [m for m in st.session_state[openai_messages] if m["role"] != "system"]:
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
        if prompt := st.chat_input("Chat with OpenAI ChatGPT..."):
            st.session_state[openai_messages].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"""
                            <div class='st-chat-message'>
                                {prompt}
                            </div>
                        """, unsafe_allow_html=True)
            asyncio.run(chat_helper.chat(LLM_CHOICE.OPENAI, st.session_state["session_api_key"],
                                         st.session_state[openai_messages],
                                         conversation_assistant.get_conversation_id()))


openai_chat()
