from typing import List, Dict
from enum import Enum
from llm.llm_chat_client import LLMChatClient
from llm.llm_openai_chat_client import OpenAIChatClient
from llm.llm_anthropic_chat_client import AnthropicChatClient

class LLM_CHOICE(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

def get_llm_client(choice: LLM_CHOICE) -> LLMChatClient:
    if choice == LLM_CHOICE.OPENAI:
        return OpenAIChatClient()
    elif choice == LLM_CHOICE.ANTHROPIC:
        return AnthropicChatClient()
    else:
        raise ValueError("Unsupported LLM choice")


def create_start_message(user_prompt: str) -> List[Dict[str, str]]:
    """
    Given a user prompt, create a conversation history with the following format:
    `[ { "role": "user", "content": user_prompt } ]`

    :param user_prompt: a user prompt string
    :return: a conversation history
    """
    return [{"role": "user", "content": user_prompt}]
