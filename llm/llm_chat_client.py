# llm_chat_client.py

from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Tuple

class LLMChatClient(ABC):
    @abstractmethod
    def converse_sync(self, prompt: str, messages: List[Dict[str, str]], model: str) -> Tuple[str, List[Dict[str, str]]]:
        pass

    @abstractmethod
    async def converse(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        Given a conversation history, generate an iterative response of strings from the LLM model.

        :param messages: a conversation history with the following format:
        `[ { "role": "user", "content": "Hello, how are you?" },
           { "role": "assistant", "content": "I am doing well, how can I help you today?" } ]`

        :return: a generator of delta string responses
        """
        pass
