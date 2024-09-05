import streamlit as st

import helpers.sidebar
from args_parser import parse_args

parse_args()

st.set_page_config(
    page_title="AI Tools Chat",
    page_icon="🎙",
    layout="wide"
)


helpers.sidebar.show()

st.toast("Welcome to AI Tools Chat!", icon="🎙️")

st.markdown("""
# Welcome to AI Tools Chat!

We are providing this more interesting web interface to let you
interact with LLM models more naturally rather than using Python
all the time!
""")

st.markdown("""
## Current Features

* **OpenAI Chat**: Chat with a fixed OpenAI model (gpt-3.5-turbo).
* **Claude Chat**: Chat with a fixed Anthropic Claude model (claude-3-haiku-20240307).

## Coming Soon Features

_We hope to add these features soon._
* Login to automatically save chat history.
* **Llama Chat**: Chat with a local VT-run llama model (tbd).

## Feedback

Please provide feedback to the current class Piazza forum.
""")
