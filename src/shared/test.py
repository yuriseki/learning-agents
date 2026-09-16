#!/usr/bin/env python3
"""
Verification script for shared module.

Tests:
    1. All imports resolve without errors
    2. Config provides sensible defaults
    3. Config respects environment variables
    4. Search tool returns expected format

Usage:
    python3 test.py
"""

import os
import sys


def test_imports() -> None:
    """Test that all imports resolve."""
    print("Testing imports...")

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
    from shared.tools import search_web, TOOLS, SEARCH_TOOL_SCHEMA

    print("  ✓ All imports resolved")


def test_config_defaults() -> None:
    """Test that config provides sensible defaults."""
    print("Testing config defaults...")

    from shared.config import LLM_BASE_URL, LLM_MODEL, LLM_API_KEY, LLM_EXTRA_BODY

    assert LLM_BASE_URL.startswith("http://"), f"Base URL should start with http://: {LLM_BASE_URL}"
    assert LLM_MODEL != "", "Model should not be empty"
    assert LLM_API_KEY != "", "API key should not be empty"
    assert isinstance(LLM_EXTRA_BODY, dict), "Extra body should be a dict"

    print(f"  ✓ Base URL: {LLM_BASE_URL}")
    print(f"  ✓ Model: {LLM_MODEL}")
    print(f"  ✓ API Key: {LLM_API_KEY}")
    print(f"  ✓ Extra Body: {LLM_EXTRA_BODY}")


def test_config_env_vars() -> None:
    """Test that config respects environment variables."""
    print("Testing config env vars...")

    # Set custom env vars
    os.environ["LLM_BASE_URL"] = "http://custom:9999/v1"
    os.environ["LLM_MODEL"] = "custom-model"
    os.environ["LLM_API_KEY"] = "custom-key"

    # Re-import to pick up new env vars
    import importlib

    import shared.config

    importlib.reload(shared.config)

    assert shared.config.LLM_BASE_URL == "http://custom:9999/v1"
    assert shared.config.LLM_MODEL == "custom-model"
    assert shared.config.LLM_API_KEY == "custom-key"

    # Reset to defaults
    del os.environ["LLM_BASE_URL"]
    del os.environ["LLM_MODEL"]
    del os.environ["LLM_API_KEY"]
    importlib.reload(shared.config)

    print("  ✓ Env vars respected")


def test_tools_schema() -> None:
    """Test that tool schemas are valid."""
    print("Testing tool schemas...")

    from shared.tools import TOOLS, SEARCH_TOOL_SCHEMA

    assert len(TOOLS) > 0, "TOOLS should not be empty"
    assert "function" in SEARCH_TOOL_SCHEMA, "Tool should have 'function' key"
    assert SEARCH_TOOL_SCHEMA["function"]["name"] == "search_web"
    assert "parameters" in SEARCH_TOOL_SCHEMA["function"]

    print(f"  ✓ {len(TOOLS)} tool(s) defined")
    print(f"  ✓ Search tool schema valid")


def test_search_format() -> None:
    """Test that search returns expected format (may fail without internet)."""
    print("Testing search format...")

    from shared.tools import search_web

    # Test error handling (no import error expected)
    result = search_web("test query", max_results=1)
    assert isinstance(result, str), "Search result should be a string"
    assert len(result) > 0, "Search result should not be empty"

    print(f"  ✓ Search returned {len(result)} chars")
    print(f"  ✓ Result preview: {result[:80]}...")


def main() -> None:
    """Run all tests."""
    print("=" * 60)
    print("Shared Module Verification")
    print("=" * 60)

    try:
        test_imports()
        test_config_defaults()
        test_config_env_vars()
        test_tools_schema()
        test_search_format()

        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0

    except Exception as e:
        print("=" * 60)
        print(f"Test failed: {type(e).__name__}: {e}")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
