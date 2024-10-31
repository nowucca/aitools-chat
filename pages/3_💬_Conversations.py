import asyncio
import os
import uuid

import streamlit as st

import helpers.sidebar
import services
from helpers import chat_helper
from helpers.auth import require_authentication, authenticated_user
from llm import prompts
from llm.llm import LLM_CHOICE

from services import conversations

@require_authentication
def conversations():
    st.set_page_config(
        page_title="Conversations",
        page_icon="💬",
        layout="wide"
    )
    user = authenticated_user()
    helpers.sidebar.show()
    st.header(f"Conversations for {user}")

    action_ctr = st.empty()

    user_conversations = services.conversations.conversations_by_user(user)

    # Custom CSS for gridline styling
    st.markdown("""
        <style>
        /* Table styling with gridlines */
        .conversation-table {
            display: grid;
            grid-template-columns: 2fr 2fr 3fr 1fr 1fr;
            width: 100%;
            border-collapse: collapse;
        }
        .conversation-header, .conversation-row {
            display: contents;
        }
        .conversation-separator-rule {
            border-bottom: 6px solid #dcdcdc;
        }
        .conversation-cell, .conversation-header-cell {
            padding: 10px;
            display: flex;
            align-items: left;
            justify-content: left;
        }
        .conversation-header-cell {
            font-weight: bold;
            background-color: #dcdcdc;
        }
        .preview-link {
            color: gray;
            text-decoration: none;
        }
        .stButton button {
            padding: 3px 8px;
            font-size: 0.8em;
        }
        </style>
    """, unsafe_allow_html=True)

    # Table Header
    st.markdown("""
    <div class="conversation-table">
        <div class="conversation-header">
            <div class="conversation-header-cell">Created Timestamp</div>
            <div class="conversation-header-cell">Model</div>
            <div class="conversation-header-cell">Preview Message</div>
            <div class="conversation-header-cell">Rejoin</div>
            <div class="conversation-header-cell">Delete</div>
        </div>
    """, unsafe_allow_html=True)

    # Display conversations with Streamlit buttons for actions
    for i, conversation in enumerate(user_conversations):
        first_message = next((msg['content'] for msg in conversation['messages'] if msg['role'] != 'system'), "")
        preview_message = (first_message[:100] + '...') if len(first_message) > 100 else first_message

        # Row content with buttons and gridlines
        col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 1, 1])

        with col1:
            st.markdown(f"<div class='conversation-cell'>{conversation['created_ts']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='conversation-cell'>{conversation['model']}</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='conversation-cell'><span class='preview-link'>{preview_message}</span></div>", unsafe_allow_html=True)
        with col4:
            if st.button('Rejoin', key=f"rejoin_{conversation['conversation_id']}"):
                with action_ctr:
                    with st.spinner(f"Rejoining conversation {conversation['conversation_id']}..."):
                        if conversation['organization'] == 'openai':
                            conversation_assistant = chat_helper.ConversationHelper("openai_conversation_id")
                            conversation_assistant.set_conversation_id(conversation['conversation_id'])
                            st.session_state.openai_messages = conversation['messages']
                            st.switch_page("pages/1_💬_OpenAI_Chat.py")
                        else:
                            conversation_assistant = chat_helper.ConversationHelper("anthropic_conversation_id")
                            conversation_assistant.set_conversation_id(conversation['conversation_id'])
                            st.session_state.anthropic_messages = conversation['messages']
                            st.switch_page("pages/2_💬_Anthropic_Chat.py")

        with col5:
            if st.button('Delete', key=f"delete_{conversation['conversation_id']}"):
                with action_ctr:
                    with st.spinner(f"Deleting conversation {conversation['conversation_id']}..."):
                        services.conversations.delete_conversation(user, conversation['conversation_id'])
                        if conversation['organization'] == 'openai':
                            conversation_assistant = chat_helper.ConversationHelper("openai_conversation_id")
                            conversation_assistant.set_conversation_id(None)
                            st.session_state.openai_messages = []
                        else:
                            conversation_assistant = chat_helper.ConversationHelper("anthropic_conversation_id")
                            conversation_assistant.set_conversation_id(None)
                            st.session_state.anthropic_messages = []
                        st.rerun()

        # Expander for full-width conversation messages
        with st.expander("View Full Conversation", expanded=False):
            for message in [m for m in conversation['messages'] if m["role"] != "system"]:
                with st.chat_message(message["role"]):
                    st.markdown(f"""
                        <div class='st-chat-message'>
                            {message['content']}
                        </div>
                    """, unsafe_allow_html=True)
        st.markdown("<p class='conversation-separator-rule'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # Close the conversation-table div

conversations()
