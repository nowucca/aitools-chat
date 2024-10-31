import asyncio
from typing import List, Dict, Union, Tuple

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from helpers.auth import authenticated_user, is_authenticated
from llm.llm import LLM_CHOICE, get_llm_client
from llm.llm_chat_client import LLMChatClient
from services.conversations import save_conversation


async def _run_conversation(client: LLMChatClient,
                           messages: List[Dict[str, str]],
                           message_placeholder: Union[DeltaGenerator, None] = None) \
        -> Tuple[List[Dict[str, str]], str]:
    full_response = ""

    chunks = client.converse(messages)
    chunk = await anext(chunks, "END OF CHAT")
    while chunk != "END OF CHAT":
        print(f"Received chunk from LLM service: {chunk}")
        if chunk.startswith("EXCEPTION"):
            full_response = ":red[We are having trouble generating advice.  Please wait a minute and try again.]"
            break
        full_response += chunk

        if message_placeholder is not None:
            message_placeholder.code(full_response + "▌")

        chunk = await anext(chunks, "END OF CHAT")

    if message_placeholder is not None:
        message_placeholder.code(full_response)

    messages.append({"role": "assistant", "content": full_response})
    return messages, full_response


# Chat with the LLM, and update the messages list with the response.
# Handles the chat UI and partial responses along the way.
async def chat(llm_choice: LLM_CHOICE,
               messages: List[Dict[str,str]],
               conversation_id: str,
               record_ok: bool = True) -> List[Dict[str,str]]:

    client: LLMChatClient = get_llm_client(llm_choice)

    message_placeholder = st.empty()
    spinner_placeholder = st.empty()

    with st.chat_message("assistant"):
        # Step 1: Display spinner while processing the response
        with spinner_placeholder:
            with st.spinner("Receiving response..."):
                messages, response = await _run_conversation(client, messages, message_placeholder)

        message_placeholder.empty()  # Clear the streamed chunks
        spinner_placeholder.empty()  # Clear the spinner

        # Display the final response
        st.write(response)

        # Save the conversation to the database
        if is_authenticated() and record_ok:
            try:
                user = authenticated_user()
                save_conversation(conversation_id, user, llm_choice.value, client.model_name(), messages)
            except Exception as e:
                st.warning(f"Temporarily failed to save conversation: {e}")

        st.session_state.messages = messages
    return messages


class ConversationHelper:
    def __init__(self, session_attr_name: str):
        self.session_attr_name = session_attr_name

    def get_conversation_id(self) -> str:
        return st.session_state.get(self.session_attr_name, None)

    def set_conversation_id(self, conversation_id: str|None):
        st.session_state[self.session_attr_name] = conversation_id

    def has_conversation_id(self) -> bool:
        return hasattr(st.session_state, self.session_attr_name) and self.session_attr_name in st.session_state
