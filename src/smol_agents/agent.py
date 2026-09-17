"""
Agent definitions for Smolagents.

The CodeAgent writes and executes Python code to achieve goals. Unlike
JSON-based tool calling, the agent has full Python expressiveness: loops,
conditionals, string formatting, data processing — all within a sandbox.

Key parameters:
    - additional_authorized_imports: whitelist of allowed Python modules
    - max_steps: safety cap on code execution steps (prevents infinite loops)
    - tools: list of tool functions available to the agent
"""

# Import framework BEFORE adding src/ to path (avoids shadowing)
import smolagents as _smolagents
CodeAgent = _smolagents.CodeAgent
LiteLLMModel = _smolagents.LiteLLMModel
DuckDuckGoSearchTool = _smolagents.DuckDuckGoSearchTool

import sys
from pathlib import Path

# Add src/ to path for shared module import
_SRC_ROOT = Path(__file__).resolve().parent.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from shared.config import (
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_API_KEY,
    LLM_TEMPERATURE,
    LLM_EXTRA_BODY,
)


def create_model():
    """Create LiteLLMModel pointing to llama.cpp.

    The 'openai/' prefix tells LiteLLM to use OpenAI-compatible API format.
    Without it, LiteLLM might try HuggingFace or another provider.

    Returns:
        Configured LiteLLMModel instance.
    """
    return LiteLLMModel(
        model_id="openai/" + LLM_MODEL,
        api_base=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        custom_llm_provider="openai",
        temperature=LLM_TEMPERATURE,
        # Disable thinking mode for Qwen3.x UD (reasoning) models
        extra_params={"chat_template_kwargs": {"enable_thinking": False}},
    )


def create_researcher():
    """Create a Researcher agent with web search tools.

    The agent writes Python code like:
        results = web_search(query="Python 3.13 release")
        # process results with whitelisted imports

    Returns:
        Configured CodeAgent instance.
    """
    return CodeAgent(
        tools=[DuckDuckGoSearchTool()],
        model=create_model(),
        # Whitelist imports — only these modules can be imported in generated code
        additional_authorized_imports=[
            "math",           # Math operations
            "json",           # JSON parsing
            "re",             # Regular expressions
            "statistics",     # Statistical functions
            "collections",    # Data structures
        ],
        max_steps=10,        # Safety cap: max 10 code execution steps
        name="Researcher",
        description="An agent that searches the web and analyzes data using Python code.",
    )


def create_writer():
    """Create a Writer agent for formatting reports.

    No tools needed — just formats text using Python code.

    Returns:
        Configured CodeAgent instance.
    """
    return CodeAgent(
        tools=[],  # Writer doesn't need tools — just formats text
        model=create_model(),
        max_steps=5,
        name="Writer",
        description="An agent that writes structured reports from research data.",
    )


def run_pipeline(topic: str) -> str:
    """Run Researcher -> Writer pipeline.

    Multi-agent is manual composition: research_result string -> writer.run()

    Args:
        topic: The research topic.

    Returns:
        The final formatted report.
    """
    print(f"\n{'=' * 60}")
    print(f"Smolagents Pipeline: Research -> Write")
    print(f"Topic: {topic}")
    print(f"{'=' * 60}\n")

    # Step 1: Research (agent writes code to search and analyze)
    researcher = create_researcher()
    research_result = researcher.run(
        f"Search for information about: {topic}. "
        f"Write Python code to process the search results and extract key facts. "
        f"Return a structured summary."
    )
    print(f"\n[Researcher] Result:\n{research_result}\n")

    # Step 2: Write report (agent writes code to format text)
    writer = create_writer()
    final_report = writer.run(
        f"Write a well-structured report based on these research findings:\n\n"
        f"{research_result}\n\n"
        f"Include: Title, Executive Summary, Key Findings, Conclusion."
    )
    print(f"\n[Writer] Final Report:\n{final_report}\n")

    return str(final_report)
