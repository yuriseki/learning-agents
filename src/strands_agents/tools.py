"""
Tool definitions for Strands Agents.

Each tool is a Python function decorated with @tool. The decorator automatically
extracts the function name, type hints, and docstring to build the JSON schema
that the LLM sees. No manual schema definition needed.

Compare to from-scratch:
    - From-scratch: manual JSON schemas + dispatch map + whitelist
    - Strands: @tool decorator handles everything

Usage:
    from strands_agents.tools import search_web, read_file, write_file
"""

from typing import Optional

from strands import tool
from shared.tools import search_web as _search_web


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """Search the web for information about a topic.

    Args:
        query: The search query string. Be specific for better results.
        max_results: Maximum number of results to return (default: 5).

    Returns:
        Formatted search results or an error message.
    """
    return _search_web(query, max_results=max_results)


@tool
def read_file(filepath: str) -> Optional[str]:
    """Read the contents of a file.

    Args:
        filepath: Absolute or relative path to the file to read.

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


@tool
def write_file(filepath: str, content: str) -> str:
    """Write content to a file. Creates parent directories if needed.

    Args:
        filepath: Absolute or relative path to the file to write.
        content: The text content to write to the file.

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
