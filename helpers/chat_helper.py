import asyncio
from typing import List, Dict, Union, Tuple

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from llm.llm import LLM_CHOICE, get_llm_client
from llm.llm_chat_client import LLMChatClient


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
               messages: List[Dict[str,str]]) -> List[Dict[str,str]]:

    client = get_llm_client(llm_choice)

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

        st.session_state.messages = messages
    return messages
