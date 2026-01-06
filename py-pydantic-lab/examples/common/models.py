"""
Model Abstraction Layer - Architectural Rationale:
--------------------------------------------------
This module implements the 'Factory Pattern' to decouple Agent logic from LLM providers.

1. Separation of Concerns: Agent defines 'what' to do (prompts, tools), while this
   factory defines 'how' to connect to the brain (DeepSeek, OpenAI, etc.).
2. Open/Closed Principle: Adding a new LLM provider only requires adding a branch 
   here, without touching existing Agent code.
3. Environment Adaptability: Seamlessly switch between local testing (DeepSeek) 
   and production (OpenAI) via environment variables.
4. Fail-Fast Validation: Ensures all required API keys are present at startup.
"""

import os
import httpx
from enum import Enum
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

class LLMProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    OLLAMA = "ollama"
    AZURE_AD = "azure_ad"
    GEMINI_VERTEX = "gemini_vertex"
    CUSTOM = "custom"

# Global singleton client for connection pooling
_shared_http_client: Optional[httpx.AsyncClient] = None

def _get_http_client() -> Optional[httpx.AsyncClient]:
    """
    Helper to create/retrieve a singleton AsyncClient with proxy settings.
    Implements connection pooling for high performance.
    """
    global _shared_http_client
    proxy_url = os.getenv('LLM_PROXY_URL')
    
    if not proxy_url:
        return None
        
    if _shared_http_client is None:
        # Optimization: Use singleton pattern to reuse connection pool
        _shared_http_client = httpx.AsyncClient(
            proxy=proxy_url,
            # Production-grade settings:
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            timeout=httpx.Timeout(60.0)
        )
    return _shared_http_client

# Factory pattern: Unified interface for multiple LLM providers.
# This ensures that switching between providers is a one-line change.
def get_model(provider_override: Optional[str] = None):
    """
    Returns a model instance based on environment variables.
    Implements validation and type safety.
    """
    # Load .env from root
    root_env = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(dotenv_path=root_env)
    
    # Resolve provider
    provider_str = provider_override or os.getenv('LLM_PROVIDER', LLMProvider.DEEPSEEK)
    try:
        provider = LLMProvider(provider_str.lower())
    except ValueError:
        raise ValueError(f"Unsupported provider: {provider_str}. Valid options: {[e.value for e in LLMProvider]}")

    if provider == LLMProvider.DEEPSEEK:
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set in environment.")
        return OpenAIChatModel(
            'deepseek-chat',
            provider=DeepSeekProvider(api_key=api_key, http_client=_get_http_client()),
        )
        
    elif provider == LLMProvider.OPENAI:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment.")
        model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o')
        return OpenAIChatModel(
            model_name, 
            provider=OpenAIProvider(api_key=api_key, http_client=_get_http_client())
        )
        
    elif provider == LLMProvider.OLLAMA:
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')
        model_name = os.getenv('OLLAMA_MODEL_NAME', 'llama3')
        return OpenAIChatModel(
            model_name,
            provider=OllamaProvider(base_url=base_url, http_client=_get_http_client()),
        )

    elif provider == LLMProvider.AZURE_AD:
        # Azure AD Auth (Managed Identity or Client Secret)
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        from openai import AsyncAzureOpenAI
        
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview')
        model_name = os.getenv('AZURE_OPENAI_MODEL_NAME', 'gpt-4o')
        
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required for AZURE_AD provider.")
            
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), 
            "https://cognitiveservices.azure.com/.default"
        )
        
        az_client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
            http_client=_get_http_client()
        )
        
        return OpenAIChatModel(
            model_name,
            provider=AzureProvider(openai_client=az_client)
        )
        
    elif provider == LLMProvider.GEMINI_VERTEX:
        project = os.getenv('GOOGLE_PROJECT_ID')
        location = os.getenv('GOOGLE_LOCATION', 'us-central1')
        model_name = os.getenv('GOOGLE_MODEL_NAME', 'gemini-1.5-pro')
        
        if not project:
            raise ValueError("GOOGLE_PROJECT_ID is required for GEMINI_VERTEX provider.")
            
        return GoogleModel(
            model_name,
            provider=GoogleProvider(
                vertexai=True,
                project=project,
                location=location,
                http_client=_get_http_client()
            )
        )
        
    elif provider == LLMProvider.CUSTOM:
        base_url = os.getenv('LLM_BASE_URL')
        api_key = os.getenv('LLM_API_KEY')
        model_name = os.getenv('LLM_MODEL_NAME')
        
        if not all([base_url, api_key, model_name]):
            raise ValueError("For CUSTOM provider, LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL_NAME must all be set.")
            
        return OpenAIChatModel(
            model_name, 
            provider=OpenAIProvider(
                base_url=base_url, 
                api_key=api_key, 
                http_client=_get_http_client()
            )
        )
