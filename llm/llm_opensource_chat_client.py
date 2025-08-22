from llm.llm_chat_client import LLMChatClient
from openai import AsyncOpenAI, OpenAI, OpenAIError
from typing import List, Dict, AsyncGenerator, Tuple

import os
import traceback

class OpensourceChatClient(LLMChatClient):
    def __init__(self):
        super().__init__()
        self.base_url = os.getenv('OPENSOURCE_API_BASE_URL')
        self.model = os.getenv('OPENSOURCE_MODEL')
        print(f"Opensource base url: {self.base_url}")
        print(f"Opensource model: {self.model}")
        print(f"Opensource proxy login URL: {self.proxy_login_url}")

    def model_name(self) -> str:
        return self.model

    def converse_sync(self, proxy_login_credentials: str, llm_api_key: str, prompt: str, messages: List[Dict[str, str]], model=None) -> Tuple[str, List[Dict[str, str]]]:
        if model is None:
            model = self.model
            
        proxy_login_token = self.proxy_login(proxy_login_credentials)
        # OpenAI client automatically appends /v1, so use base_url directly
        client = OpenAI(api_key=proxy_login_token, base_url=self.base_url)
        
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

    async def converse(self, proxy_login_credentials: str, llm_api_key: str, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        proxy_login_token = self.proxy_login(proxy_login_credentials)
        
        # For opensource, we don't need the user's API key, so we ignore llm_api_key parameter
        # OpenAI client automatically appends /v1, so use base_url directly
        aclient = AsyncOpenAI(api_key=proxy_login_token, base_url=self.base_url)
        
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
