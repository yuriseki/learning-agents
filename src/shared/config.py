"""
Shared LLM Configuration

Provides environment-variable-based configuration for all framework packages.
Each framework adapts these raw values to its own API (openai, langchain-openai, litellm, etc.).

Usage:
    from shared.config import LLM_BASE_URL, LLM_MODEL, LLM_API_KEY, LLM_EXTRA_BODY

Environment Variables:
    LLM_BASE_URL    — OpenAI-compatible API endpoint (default: localhost:8123)
    LLM_MODEL       — Model name/ID (default: Qwen3.6-27B)
    LLM_API_KEY     — API key (default: not-needed for local models)
    LLM_MAX_TOKENS  — Max output tokens (default: 4096)
    LLM_TEMPERATURE — Sampling temperature (default: 0.7)
    LLM_DISABLE_THINKING — Disable reasoning/thinking mode (default: true)
"""

import os
from typing import Any


# ─────────────────────────────────────────────
# Core Configuration
# ─────────────────────────────────────────────

def get_llm_base_url() -> str:
    """Get the LLM endpoint URL.

    Supports both host (localhost) and Docker sandbox (172.17.0.1) environments.
    Override with LLM_BASE_URL environment variable.

    Returns:
        URL of the OpenAI-compatible API endpoint.
    """
    return os.environ.get("LLM_BASE_URL", "http://localhost:8124/v1")


def get_llm_model() -> str:
    """Get the model name/ID.

    Override with LLM_MODEL environment variable.

    Returns:
        Model identifier (e.g., 'Qwen3.6-27B', 'Qwen3.8-27B-UD-Q3_K_XL.gguf').
    """
    return os.environ.get("LLM_MODEL", "Qwen3.6-27B")


def get_llm_api_key() -> str:
    """Get the API key.

    For local models (llama.cpp), this is typically 'not-needed'.
    Override with LLM_API_KEY environment variable.

    Returns:
        API key string.
    """
    return os.environ.get("LLM_API_KEY", "not-needed")


# ─────────────────────────────────────────────
# Optional Configuration
# ─────────────────────────────────────────────

def get_llm_max_tokens() -> int:
    """Get the maximum output tokens.

    Override with LLM_MAX_TOKENS environment variable.

    Returns:
        Maximum number of output tokens (default: 4096).
    """
    return int(os.environ.get("LLM_MAX_TOKENS", "4096"))


def get_llm_temperature() -> float:
    """Get the sampling temperature.

    Override with LLM_TEMPERATURE environment variable.

    Returns:
        Temperature value (default: 0.7).
    """
    return float(os.environ.get("LLM_TEMPERATURE", "0.7"))


def get_llm_extra_body() -> dict[str, Any]:
    """Get extra body parameters for the LLM API call.

    Reasoning models (Qwen3.8, etc.) require `enable_thinking: False` to avoid
    empty responses. Override with LLM_DISABLE_THINKING environment variable.

    Returns:
        Dict of extra parameters (default: disables thinking mode).
    """
    disable_thinking = os.environ.get("LLM_DISABLE_THINKING", "true").lower() == "true"
    if disable_thinking:
        return {"chat_template_kwargs": {"enable_thinking": False}}
    return {}


# ─────────────────────────────────────────────
# Convenience: Raw values for frameworks that need them
# ─────────────────────────────────────────────

LLM_BASE_URL: str = get_llm_base_url()
LLM_MODEL: str = get_llm_model()
LLM_API_KEY: str = get_llm_api_key()
LLM_MAX_TOKENS: int = get_llm_max_tokens()
LLM_TEMPERATURE: float = get_llm_temperature()
LLM_EXTRA_BODY: dict[str, Any] = get_llm_extra_body()
