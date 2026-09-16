"""
Tool definitions for the from-scratch ReAct agent.

Each tool has three parts:
    1. A Python function (the actual implementation)
    2. A JSON schema (what the LLM sees to know what tools exist)
    3. A whitelist check (security boundary — only approved tools can run)

The LLM uses the JSON schemas to decide which tool to call and what arguments
to pass. We then map the tool name back to the Python function and execute it.

This module reuses tools from `shared.tools` and adds framework-specific ones.
"""

from typing import Any, Optional

from shared.tools import search_web as _search_web, format_tool_definition

# =============================================================================
# Tool Implementations
# =============================================================================


def search_web(query: str, max_results: int = 5) -> str:
    """Search the web for information about a topic.

    Args:
        query: The search query string.
        max_results: Maximum number of results (default: 5).

    Returns:
        Formatted search results or an error message.
    """
    return _search_web(query, max_results=max_results)


def read_file(filepath: str) -> Optional[str]:
    """Read the contents of a file.

    Args:
        filepath: Path to the file to read.

    Returns:
        The file contents, or an error message.
    """
    from pathlib import Path

    try:
        return Path(filepath).read_text()
    except FileNotFoundError:
        return f"File not found: {filepath}"
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(filepath: str, content: str) -> str:
    """Write content to a file.

    Args:
        filepath: Path to the file to write.
        content: Content to write to the file.

    Returns:
        A success message or an error message.
    """
    from pathlib import Path

    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).write_text(content)
        return f"Successfully wrote to {filepath} ({len(content)} chars)"
    except Exception as e:
        return f"Error writing file: {e}"


# =============================================================================
# Tool Schemas (what the LLM sees)
# =============================================================================

TOOLS = [
    format_tool_definition(
        name="search_web",
        description=(
            "Search the web for information about a topic. "
            "Returns up to 5 relevant results with titles and summaries."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string. Be specific for better results.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5).",
                    "minimum": 1,
                    "maximum": 20,
                },
            },
            "required": ["query"],
        },
    ),
    format_tool_definition(
        name="read_file",
        description="Read the contents of a file. Returns the full text content.",
        parameters={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read.",
                },
            },
            "required": ["filepath"],
        },
    ),
    format_tool_definition(
        name="write_file",
        description="Write text content to a file. Creates parent directories if needed.",
        parameters={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write to the file.",
                },
            },
            "required": ["filepath", "content"],
        },
    ),
]


# =============================================================================
# Tool Dispatch (maps tool names to Python functions)
# =============================================================================

TOOL_FUNCTIONS: dict[str, Any] = {
    "search_web": search_web,
    "read_file": read_file,
    "write_file": write_file,
}

# Explicit whitelist — only these tools can be called
APPROVED_TOOLS = set(TOOL_FUNCTIONS.keys())


def safe_execute_tool(function_name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool only if it's in the approved whitelist.

    This is the security boundary. Even if the LLM tries to call a
    tool not in APPROVED_TOOLS, it will be blocked.

    Args:
        function_name: Name of the tool to call.
        arguments: Dict of arguments to pass to the tool.

    Returns:
        The tool's output as a string, or an error message.
    """
    if function_name not in APPROVED_TOOLS:
        return f"BLOCKED: Tool '{function_name}' is not approved. Available: {APPROVED_TOOLS}"

    if function_name not in TOOL_FUNCTIONS:
        return f"ERROR: Tool '{function_name}' not found in dispatch map."

    try:
        return str(TOOL_FUNCTIONS[function_name](**arguments))
    except Exception as e:
        return f"ERROR executing '{function_name}': {e}"
