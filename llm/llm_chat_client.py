# llm_chat_client.py

from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Tuple, Optional
import httpx
import os
import base64
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class LLMChatClientError(Exception):
    """Base exception for LLMChatClient errors."""
    pass

class AuthenticationError(LLMChatClientError):
    """Raised when authentication fails."""
    pass

class LLMChatClient(ABC):
    def __init__(self, proxy_login_url: Optional[str] = None):
        self.proxy_login_url = proxy_login_url or os.getenv('AITOOLS_CHAT_PROXY_LOGIN_URL')
        
        if not self.proxy_login_url:
            raise ValueError("Proxy login URL must be provided either as parameter or AITOOLS_CHAT_PROXY_LOGIN_URL environment variable")
        
        # Don't log potentially sensitive URLs in production
        logger.debug(f"Initialized LLM client with proxy URL: {self.proxy_login_url}")
        
        # Use context manager for proper resource management
        self._http_client = None

    @contextmanager
    def _get_http_client(self):
        """Context manager for HTTP client to ensure proper cleanup."""
        if self._http_client is None:
            self._http_client = httpx.Client(timeout=30.0)
        try:
            yield self._http_client
        finally:
            # Keep client alive for reuse, but ensure it can be closed when needed
            pass

    def close(self):
        """Explicitly close the HTTP client."""
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def proxy_login(self, proxy_login_credentials: str) -> str:
        """
        Authenticate with the proxy server and return the authentication token.
        
        :param proxy_login_credentials: Base64-encoded credentials in format "username:pin"
        :return: Authentication token from proxy server
        :raises: AuthenticationError if authentication fails
        :raises: LLMChatClientError for other client errors
        """
        try:
            # Decode base64 credentials if they appear to be encoded
            if self._is_base64_encoded(proxy_login_credentials):
                decoded_credentials = base64.b64decode(proxy_login_credentials).decode('utf-8')
            else:
                decoded_credentials = proxy_login_credentials
            
            # Parse the credentials
            if ':' not in decoded_credentials:
                raise ValueError("Credentials must be in format 'username:pin'")
            
            username, pin = decoded_credentials.split(':', 1)  # Split only on first ':'
            print(f"Using username: {username} and pin: {pin}")  # Debugging output
            
            if not username or not pin:
                raise ValueError("Both username and pin must be non-empty")

            # Prepare request payload with parsed credentials
            request_payload = {"username": username, "pin": pin}
            
            with self._get_http_client() as client:
                try:
                    response = client.post(
                        self.proxy_login_url,
                        json=request_payload
                    )
                    response.raise_for_status()
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 401:
                        raise AuthenticationError("Invalid credentials") from e
                    elif e.response.status_code == 403:
                        raise AuthenticationError("Access forbidden") from e
                    else:
                        raise LLMChatClientError(f"HTTP error {e.response.status_code}: {e.response.text}") from e
                
                except httpx.RequestError as e:
                    raise LLMChatClientError(f"Request failed: {str(e)}") from e

            # Parse response
            try:
                response_data = response.json()
                token = response_data.get("token")
                
                if not token:
                    raise LLMChatClientError("No token received from server")
                
                return token
                
            except ValueError as e:
                raise LLMChatClientError("Invalid JSON response from server") from e
        
        except ValueError as e:
            raise LLMChatClientError(f"Invalid credentials format: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (AuthenticationError, LLMChatClientError)):
                raise
            raise LLMChatClientError(f"Unexpected error during authentication: {str(e)}") from e

    def _is_base64_encoded(self, data: str) -> bool:
        """Check if string appears to be base64 encoded."""
        try:
            # Base64 strings should be valid when decoded
            if len(data) % 4 == 0:  # Base64 length is always multiple of 4
                decoded = base64.b64decode(data, validate=True)
                # Check if decoded data contains only printable ASCII (typical for credentials)
                return all(32 <= b <= 126 for b in decoded)
        except Exception:
            pass
        return False
    
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the LLM model."""
        pass

    @abstractmethod
    def converse_sync(
        self, 
        proxy_login_credentials: str, 
        llm_api_key: str, 
        prompt: str, 
        messages: List[Dict[str, str]], 
        model: str
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Synchronous conversation with the LLM.
        
        :param proxy_login_credentials: Credentials for proxy authentication
        :param llm_api_key: API key for the LLM service
        :param prompt: The prompt to send
        :param messages: Conversation history
        :param model: Model to use
        :return: Tuple of (response, updated_messages)
        """
        pass

    @abstractmethod
    async def converse(
        self, 
        proxy_login_credentials: str, 
        llm_api_key: str, 
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """
        Given a conversation history, generate an iterative response of strings from the LLM model.

        :param proxy_login_credentials: Credentials for proxy authentication
        :param llm_api_key: API key for the LLM service
        :param messages: A conversation history with the following format:
            `[ { "role": "user", "content": "Hello, how are you?" },
               { "role": "assistant", "content": "I am doing well, how can I help you today?" } ]`

        :return: A generator of delta string responses
        """
        pass
