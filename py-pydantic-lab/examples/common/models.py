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
from enum import Enum
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.ollama import OllamaProvider

class LLMProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    OLLAMA = "ollama"
    CUSTOM = "custom"

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
            provider=DeepSeekProvider(api_key=api_key),
        )
        
    elif provider == LLMProvider.OPENAI:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment.")
        model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o')
        return OpenAIChatModel(model_name, api_key=api_key)
        
    elif provider == LLMProvider.OLLAMA:
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')
        model_name = os.getenv('OLLAMA_MODEL_NAME', 'llama3')
        return OpenAIChatModel(
            model_name,
            provider=OllamaProvider(base_url=base_url),
        )
        
    elif provider == LLMProvider.CUSTOM:
        base_url = os.getenv('LLM_BASE_URL')
        api_key = os.getenv('LLM_API_KEY')
        model_name = os.getenv('LLM_MODEL_NAME')
        
        if not all([base_url, api_key, model_name]):
            raise ValueError("For CUSTOM provider, LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL_NAME must all be set.")
            
        return OpenAIChatModel(model_name, base_url=base_url, api_key=api_key)
