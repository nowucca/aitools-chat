import httpx
import json
import logging
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AnthropicDebugClient:
    """Debug utility for Anthropic API calls through proxy with detailed wire-level logging."""
    
    def __init__(self, base_url: str, jwt_token: str, anthropic_api_key: str):
        self.base_url = base_url.rstrip('/')
        self.jwt_token = jwt_token
        self.anthropic_api_key = anthropic_api_key
        
        # Create HTTP client with detailed logging
        self.client = httpx.Client(
            timeout=30.0,
            event_hooks={
                'request': [self._log_request],
                'response': [self._log_response]
            }
        )
    
    def _log_request(self, request: httpx.Request):
        """Log detailed request information."""
        print(f"\n{'='*80}")
        print(f"🔵 OUTGOING REQUEST")
        print(f"{'='*80}")
        print(f"Method: {request.method}")
        print(f"URL: {request.url}")
        print(f"Headers:")
        for key, value in request.headers.items():
            # Mask sensitive tokens for security
            if 'authorization' in key.lower() or 'key' in key.lower():
                masked_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
                print(f"  {key}: {masked_value}")
            else:
                print(f"  {key}: {value}")
        
        if request.content:
            try:
                # Try to parse and pretty-print JSON
                content_str = request.content.decode('utf-8')
                parsed = json.loads(content_str)
                print(f"Body (JSON):")
                print(json.dumps(parsed, indent=2))
            except:
                print(f"Body (raw): {request.content}")
        print(f"{'='*80}\n")
    
    def _log_response(self, response: httpx.Response):
        """Log detailed response information."""
        print(f"\n{'='*80}")
        print(f"🔴 INCOMING RESPONSE")
        print(f"{'='*80}")
        print(f"Status Code: {response.status_code}")
        print(f"Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        try:
            response_json = response.json()
            print(f"Body (JSON):")
            print(json.dumps(response_json, indent=2))
        except:
            print(f"Body (text): {response.text}")
        print(f"{'='*80}\n")
    
    def test_health_check(self) -> Dict[str, Any]:
        """Test basic connectivity with health check similar to working example."""
        print("🧪 Testing Health Check (like working example)...")
        
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
            "X-User-Anthropic-Key": self.anthropic_api_key
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "messages": [
                {"role": "user", "content": "Say 'Health check successful' and nothing else."}
            ],
            "max_tokens": 10,
            "stream": False
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=payload
            )
            
            return {
                "provider": "anthropic",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "error": None if response.status_code == 200 else response.text,
                "response_data": response.json() if response.status_code == 200 else None
            }
            
        except Exception as e:
            return {
                "provider": "anthropic",
                "status_code": None,
                "success": False,
                "response_time": None,
                "error": str(e),
                "response_data": None
            }
    
    def test_streaming(self, messages: list) -> None:
        """Test streaming API call with debugging."""
        print("🧪 Testing Streaming API...")
        
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
            "X-User-Anthropic-Key": self.anthropic_api_key
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "messages": messages,
            "max_tokens": 100,
            "stream": True
        }
        
        try:
            with self.client.stream(
                "POST",
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=payload
            ) as response:
                print(f"Stream response status: {response.status_code}")
                for line in response.iter_lines():
                    if line:
                        print(f"Stream chunk: {line}")
        except Exception as e:
            print(f"Streaming error: {e}")
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()

# Quick test function
def debug_anthropic_connection():
    """Quick debugging function to test the connection."""
    from llm.llm_chat_client import LLMChatClient
    
    # You'll need to provide these values
    proxy_login_credentials = input("Enter proxy login credentials (username:pin): ")
    anthropic_api_key = input("Enter your Anthropic API key: ")
    
    # Get JWT token using the improved login
    base_client = LLMChatClient()
    try:
        jwt_token = base_client.proxy_login(proxy_login_credentials)
        print(f"✅ Successfully obtained JWT token: {jwt_token[:10]}...{jwt_token[-4:]}")
    except Exception as e:
        print(f"❌ Failed to get JWT token: {e}")
        return
    
    # Test with debug client
    base_url = os.getenv('ANTHROPIC_API_BASE_URL', 'http://aitools.cs.vt.edu:7860/anthropic')
    debug_client = AnthropicDebugClient(base_url, jwt_token, anthropic_api_key)
    
    try:
        # Test health check
        result = debug_client.test_health_check()
        print(f"\n📊 Health Check Result: {json.dumps(result, indent=2)}")
        
        if result['success']:
            print("✅ Health check passed!")
            
            # Test streaming if health check works
            test_messages = [{"role": "user", "content": "Hello, how are you?"}]
            debug_client.test_streaming(test_messages)
        else:
            print("❌ Health check failed!")
            
    finally:
        debug_client.close()

if __name__ == "__main__":
    debug_anthropic_connection()
