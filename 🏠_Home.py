import streamlit as st

import helpers.sidebar
from args_parser import parse_args

from helpers.auth import require_authentication



@require_authentication
def home():
    parse_args()

    st.set_page_config(
        page_title="AI Tools Chat",
        page_icon="🎙",
        layout="wide"
    )

    helpers.sidebar.show()

    st.markdown("""
    # Welcome to AI Tools Chat!

    We are providing this more interesting web interface to let you
    interact with LLM models more naturally rather than using Python
    all the time!
    """)

    st.markdown("""
    ## Current Features

    * **🎉 Opensource LLM Chat**: Chat with the CS5740 class LLM (DeepSeek-R1-Distill-Qwen-32B, hosted at Virginia Tech ARC) --> No API key required!
    * **OpenAI Chat**: Chat with a fixed OpenAI model (gpt-4o) --> but you need to bring your own credentials.
    * **Claude Chat**: Chat with a fixed Anthropic Claude model (claude-3-haiku-20240307) --> but you need to bring your own credentials.

    ## Coming Soon Features

    _We hope to add these features soon._
    * Nicer UI

    ## Feedback

    Please provide feedback to the current class Piazza forum.
    """)

home()
