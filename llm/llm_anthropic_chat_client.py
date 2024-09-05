from llm.llm_chat_client import LLMChatClient
import anthropic
from typing import List, Dict, AsyncGenerator, Tuple
import os
import traceback
from dotenv import load_dotenv

load_dotenv()
class AnthropicChatClient(LLMChatClient):
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.base_url = os.getenv('ANTHROPIC_API_BASE_URL')
        self.model = os.getenv('ANTHROPIC_MODEL')

        print(f"Anthropic api_key: {self.api_key}")
        print(f"Anthropic base_url: {self.base_url}")
        print(f"Anthropic model: {self.model}")

    def converse_sync(self, prompt: str, messages: List[Dict[str, str]], model="claude-2") -> Tuple[str, List[Dict[str, str]]]:
        # Initialize the Anthropic client with dummy values pointing to the proxy
        client = anthropic.Anthropic(api_key=self.api_key,
                                     base_url=self.base_url)

        # Add the user's message to the list of messages
        if messages is None:
            messages = []

        messages.append({"role": "user", "content": prompt})
        # Construct the request payload for Anthropic through the proxy
        response = client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": "Hello, world"}
            ]
        )

        # Extract the relevant information from the response
        content_text = response.content[0].text  # Access the text of the first message
        # Add the assistant's message to the list of messages
        messages.append({"role": "assistant", "content": content_text})

        return response, messages

    async def converse(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        aclient = anthropic.AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)
        # Check for a system message at the start
        system_prompt = None
        if messages and messages[0].get("role") == "system":
            system_prompt = messages[0].get("content")
            messages = messages[1:]

        try:
            async for event in await aclient.messages.create(model=self.model,
                                                             messages=messages,
                                                             max_tokens=4000,
                                                             stream=True,
                                                             system=system_prompt):
                content = None
                if event.type == 'content_block_delta':
                    content = event.delta.text
                if content:
                    yield content


        except anthropic.APIConnectionError as e:
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
            yield f"EXCEPTION The server could not be reached: {e.__cause__}"

        except anthropic.RateLimitError as e:
            yield f"EXCEPTION A 429 status code was received; we should back off a bit."

        except anthropic.APIStatusError as e:
            yield f"EXCEPTION Another non-200-range status code was received: {e.status_code}, {e.message}"

        except Exception as e:
            yield f"EXCEPTION {str(e)}"

