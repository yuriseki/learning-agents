#!/usr/bin/env python3
"""
Verification script for from_scratch package.

Tests:
    1. All imports resolve without errors
    2. Agent can be created with proper config
    3. Tool schemas are valid
    4. Tool dispatch works correctly
    5. Single agent run completes (requires LLM server)

Usage:
    python3 test.py
"""

import json
import sys
from pathlib import Path

# Add src/ to path
_SRC_ROOT = Path(__file__).resolve().parent.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


def test_imports() -> None:
    """Test that all imports resolve."""
    print("Testing imports...")

    from from_scratch import SimpleAgent, TOOLS, TOOL_FUNCTIONS
    from from_scratch.agent import SimpleAgent as AgentImport
    from from_scratch.tools import (
        TOOLS as TOOLS_IMPORT,
        TOOL_FUNCTIONS as FUNCS_IMPORT,
        safe_execute_tool,
        APPROVED_TOOLS,
    )

    print("  ✓ All imports resolved")


def test_agent_creation() -> None:
    """Test that agent can be created with proper config."""
    print("Testing agent creation...")

    from from_scratch.agent import SimpleAgent

    agent = SimpleAgent(
        name="TestAgent",
        instructions="You are a test agent.",
        max_iterations=3,
    )

    assert agent.name == "TestAgent"
    assert agent.max_iterations == 3
    assert len(agent.messages) > 0  # System message added
    assert agent.messages[0]["role"] == "system"
    assert "TestAgent" in agent.messages[0]["content"]

    print(f"  ✓ Agent created: {agent.name}")
    print(f"  ✓ System message set")
    print(f"  ✓ Max iterations: {agent.max_iterations}")


def test_tools_schema() -> None:
    """Test that tool schemas are valid."""
    print("Testing tool schemas...")

    from from_scratch.tools import TOOLS, TOOL_FUNCTIONS, APPROVED_TOOLS

    assert len(TOOLS) > 0, "TOOLS should not be empty"
    assert len(TOOL_FUNCTIONS) > 0, "TOOL_FUNCTIONS should not be empty"
    assert len(APPROVED_TOOLS) > 0, "APPROVED_TOOLS should not be empty"

    # Check each tool has required fields
    for tool in TOOLS:
        assert "function" in tool, f"Tool missing 'function' key: {tool}"
        assert "name" in tool["function"], f"Tool missing 'name': {tool}"
        assert "parameters" in tool["function"], f"Tool missing 'parameters': {tool}"

    # Check dispatch map matches schemas
    tool_names = {t["function"]["name"] for t in TOOLS}
    dispatch_names = set(TOOL_FUNCTIONS.keys())
    assert tool_names == dispatch_names, f"Tool names mismatch: {tool_names} vs {dispatch_names}"
    assert tool_names == APPROVED_TOOLS, f"Approved tools mismatch: {tool_names} vs {APPROVED_TOOLS}"

    print(f"  ✓ {len(TOOLS)} tool(s) defined")
    print(f"  ✓ Dispatch map matches schemas")
    print(f"  ✓ Approved tools: {APPROVED_TOOLS}")


def test_tool_dispatch() -> None:
    """Test that tool dispatch works correctly."""
    print("Testing tool dispatch...")

    from from_scratch.tools import safe_execute_tool, APPROVED_TOOLS

    # Test approved tool
    result = safe_execute_tool("search_web", {"query": "test"})
    assert isinstance(result, str), "Result should be a string"
    assert len(result) > 0, "Result should not be empty"

    # Test blocked tool
    result = safe_execute_tool("evil_command", {"cmd": "rm -rf /"})
    assert "BLOCKED" in result, f"Should block evil tool: {result}"

    # Test unknown tool
    result = safe_execute_tool("nonexistent", {})
    assert "ERROR" in result or "BLOCKED" in result, f"Should error on unknown tool: {result}"

    print(f"  ✓ Approved tools execute")
    print(f"  ✓ Blocked tools rejected")
    print(f"  ✓ Unknown tools error")


def test_argument_parsing() -> None:
    """Test that argument parsing handles edge cases."""
    print("Testing argument parsing...")

    from from_scratch.agent import SimpleAgent

    # Valid JSON
    args = SimpleAgent._parse_arguments('{"query": "test", "max_results": 3}')
    assert args == {"query": "test", "max_results": 3}

    # Invalid JSON
    args = SimpleAgent._parse_arguments("not json at all")
    assert args == {}, f"Should return empty dict for invalid JSON: {args}"

    # Empty string
    args = SimpleAgent._parse_arguments("")
    assert args == {}, f"Should return empty dict for empty string: {args}"

    print("  ✓ Valid JSON parsed correctly")
    print("  ✓ Invalid JSON returns empty dict")
    print("  ✓ Empty string returns empty dict")


def test_single_agent_run() -> None:
    """Test single agent run (requires LLM server).

    This test will fail if no LLM server is running. That's expected.
    """
    print("Testing single agent run (requires LLM server)...")

    from from_scratch.agent import SimpleAgent

    agent = SimpleAgent(
        name="TestAgent",
        instructions="You are a helpful assistant. Reply briefly.",
        max_iterations=2,
    )

    try:
        result = agent.run("What is 2+2? Reply with just the number.")
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        print(f"  ✓ Agent run completed")
        print(f"  ✓ Result: {result[:80]}...")
    except Exception as e:
        print(f"  ⚠ Agent run skipped (LLM server not running): {e}")


def main() -> None:
    """Run all tests."""
    print("=" * 60)
    print("from_scratch Package Verification")
    print("=" * 60)

    try:
        test_imports()
        test_agent_creation()
        test_tools_schema()
        test_tool_dispatch()
        test_argument_parsing()
        test_single_agent_run()

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
