from llm.llm_chat_client import LLMChatClient
from openai import AsyncOpenAI, OpenAI, OpenAIError
from typing import List, Dict, AsyncGenerator, Tuple

import os
import traceback

class OpenAIChatClient(LLMChatClient):
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('OPENAI_API_BASE_URL')
        self.model = os.getenv('OPENAI_API_MODEL')
        print(f"OpenAI api key: {self.api_key}")
        print(f"OpenAI base url: {self.base_url}")
        print(f"OpenAI model: {self.model}")

    def converse_sync(self, prompt: str, messages: List[Dict[str, str]], model="gpt-3.5-turbo") -> Tuple[str, List[Dict[str, str]]]:
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        # Add the user's message to the list of messages
        if messages is None:
            messages = []

        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
        ).choices[0].message.content

        # Add the assistant's message to the list of messages
        messages.append({"role": "assistant", "content": response})

        return response, messages

    async def converse(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        aclient = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        try:
            async for chunk in await aclient.chat.completions.create(model=self.model,
                                                                     messages=messages,
                                                                     max_tokens=4000,
                                                                     stream=True):
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except OpenAIError as e:
            traceback.print_exc()
            yield f"oaiEXCEPTION {str(e)}"
        except Exception as e:
            yield f"EXCEPTION {str(e)}"
