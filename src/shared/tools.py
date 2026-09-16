"""
Shared Tools

Provides common tools that all framework packages can reuse.
Currently: web search via DuckDuckGo.

Usage:
    from shared.tools import search_web, TOOLS

Each framework adapts these tools to its own API:
- From-scratch: raw dict with name/description/parameters
- Strands: @tool decorated functions
- Smolagents: Tool class with forward method
- CrewAI: BaseTool subclass
- AG2: built into agent config
- LangGraph: LangChain tool wrapper
- Pydantic AI: tool-decorated functions
"""

from typing import Optional


def search_web(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return (default: 5).

    Returns:
        Formatted string with search results (title, snippet, url).
        Returns an error message if search fails.
    """
    try:
        from ddgs import DDGS

        results = DDGS().text(query, max_results=max_results)
        if not results:
            return f"No results found for: {query}"

        lines = [f"Search results for: {query}\n"]
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            snippet = result.get("body", result.get("description", ""))
            url = result.get("href", result.get("link", ""))
            lines.append(f"{i}. {title}")
            if snippet:
                lines.append(f"   {snippet}")
            if url:
                lines.append(f"   {url}")
            lines.append("")

        return "\n".join(lines)

    except ImportError:
        return "ERROR: ddgs not installed. Install with: pip install ddgs"
    except Exception as e:
        return f"Search error: {type(e).__name__}: {e}"


def format_tool_definition(name: str, description: str, parameters: dict) -> dict:
    """Format a tool definition for OpenAI-compatible function calling.

    Args:
        name: Tool name.
        description: Tool description.
        parameters: JSON Schema for tool parameters.

    Returns:
        Dict matching OpenAI function calling format.
    """
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


# ─────────────────────────────────────────────
# Pre-defined tool schemas (for from-scratch and similar)
# ─────────────────────────────────────────────

SEARCH_TOOL_SCHEMA = format_tool_definition(
    name="search_web",
    description="Search the web using DuckDuckGo. Returns formatted search results.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string.",
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
)

# List of all available tool schemas
TOOLS = [SEARCH_TOOL_SCHEMA]
