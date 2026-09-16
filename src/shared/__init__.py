"""
Shared module for Learning AI Agents blog series.

Provides common LLM configuration and reusable tools for all framework packages.

Submodules:
    config — LLM endpoint configuration (base_url, model, api_key, extra_body)
    tools  — Common tools (web search via DuckDuckGo)
"""

from shared.config import (
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_API_KEY,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_EXTRA_BODY,
    get_llm_base_url,
    get_llm_model,
    get_llm_api_key,
    get_llm_extra_body,
)
from shared.tools import search_web, TOOLS

__all__ = [
    "LLM_BASE_URL",
    "LLM_MODEL",
    "LLM_API_KEY",
    "LLM_MAX_TOKENS",
    "LLM_TEMPERATURE",
    "LLM_EXTRA_BODY",
    "get_llm_base_url",
    "get_llm_model",
    "get_llm_api_key",
    "get_llm_extra_body",
    "search_web",
    "TOOLS",
]
