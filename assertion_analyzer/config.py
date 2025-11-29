"""
Configuration and API utilities for the Assertion Analyzer.

This module provides:
- Substrate GPT-5 JJ API configuration
- Microsoft authentication helpers
- JSON extraction utilities
"""

import os
import json
import time
import ctypes
import re
from typing import Dict, Any, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# API Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SUBSTRATE_ENDPOINT = "https://fe-26.qas.bing.net/chat/completions"
SUBSTRATE_RESOURCE = "https://substrate.office.com"
CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
JJ_MODEL = "dev-gpt-5-chat-jj"

# Rate limiting
DELAY_BETWEEN_CALLS = 2  # seconds
MAX_RETRIES = 3

# Global token cache
_jj_token_cache = None


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════════════════

def get_substrate_token() -> str:
    """
    Get authentication token for Substrate API using MSAL broker.
    
    Returns:
        Access token string
        
    Raises:
        ImportError: If msal[broker] is not installed
        Exception: If authentication fails
    """
    global _jj_token_cache
    
    if _jj_token_cache:
        return _jj_token_cache
    
    try:
        import msal
    except ImportError:
        raise ImportError(
            "msal[broker] not installed. Run: pip install msal[broker]"
        )
    
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        enable_broker_on_windows=True,
    )
    
    scopes = [f"{SUBSTRATE_RESOURCE}/.default"]
    
    # Try silent auth first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            _jj_token_cache = result["access_token"]
            return _jj_token_cache
    
    # Fall back to interactive
    print("Authenticating with Microsoft (browser may open)...")
    
    kernel32 = ctypes.windll.kernel32
    hwnd = kernel32.GetConsoleWindow()
    
    result = app.acquire_token_interactive(
        scopes,
        parent_window_handle=hwnd,
    )
    
    if "access_token" in result:
        _jj_token_cache = result["access_token"]
        return _jj_token_cache
    else:
        raise Exception(f"Authentication failed: {result.get('error_description', result)}")


def clear_token_cache():
    """Clear the cached authentication token."""
    global _jj_token_cache
    _jj_token_cache = None


# ═══════════════════════════════════════════════════════════════════════════════
# API Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def call_gpt5_api(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 4000,
    max_retries: int = MAX_RETRIES
) -> str:
    """
    Call Substrate GPT-5 JJ API with retry logic.
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens in response
        max_retries: Number of retries on rate limit
        
    Returns:
        Response text from the model
        
    Raises:
        ImportError: If requests is not installed
        Exception: If API call fails after retries
    """
    try:
        import requests
    except ImportError:
        raise ImportError("requests not installed. Run: pip install requests")
    
    token = get_substrate_token()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-ModelType": JJ_MODEL
    }
    
    payload = {
        "model": JJ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                SUBSTRATE_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            elif response.status_code == 429:
                wait_time = (attempt + 1) * 10
                print(f"  Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise Exception(f"GPT-5 API error {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"  Request timeout, retrying...")
            time.sleep(5)
    
    raise Exception(f"GPT-5 API failed after {max_retries} retries")


def extract_json_from_response(response: str) -> Dict[str, Any]:
    """
    Extract JSON from a GPT response that may contain markdown.
    
    Args:
        response: Raw response text that may contain JSON in code blocks
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        json.JSONDecodeError: If JSON parsing fails
    """
    # Try to find JSON in code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response.strip()
    
    # Clean up common issues
    json_str = json_str.strip()
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    
    return json.loads(json_str)


# ═══════════════════════════════════════════════════════════════════════════════
# File I/O Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def save_json(data: Any, filepath: str) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to serialize
        filepath: Output file path
    """
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str) -> Any:
    """
    Load data from JSON file.
    
    Args:
        filepath: Input file path
        
    Returns:
        Parsed JSON data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
