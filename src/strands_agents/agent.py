"""
Strands Agents — Model, Tools, Agent primitives.

The 3-primitive architecture:
    1. Model — connects to the LLM (OpenAI-compatible API)
    2. Tools — @tool decorated functions
    3. Agent — runs the ReAct loop internally (model-driven)

Key difference from from-scratch:
    - From-scratch: you write the ReAct loop (for loop, tool dispatch, etc.)
    - Strands: the Agent runs the loop internally. You just compose primitives.

The model drives the loop. It decides when to call tools and when to stop.
This means you have less control but less code to write.
"""

import sys
from pathlib import Path
from typing import Optional

from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator

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
from strands_agents.tools import search_web, read_file, write_file


def create_model() -> OpenAIModel:
    """Create the Model primitive pointing to llama.cpp.

    OpenAIModel with client_args connects to ANY OpenAI-compatible endpoint
    (including llama.cpp). The model_id must match what the server reports.

    Returns:
        Configured OpenAIModel instance.
    """
    return OpenAIModel(
        client_args={
            "api_key": LLM_API_KEY,
            "base_url": LLM_BASE_URL,
        },
        model_id=LLM_MODEL,
        params={
            "max_tokens": 4096,
            "temperature": LLM_TEMPERATURE,
            "extra_body": LLM_EXTRA_BODY,
        },
    )


def create_agent(
    name: str,
    instructions: str,
    tools: Optional[list] = None,
) -> Agent:
    """Create a Strands Agent with the given configuration.

    Args:
        name: Display name for the agent (used in instructions).
        instructions: System prompt defining the agent's role and behavior.
        tools: List of @tool decorated functions (default: [search_web]).

    Returns:
        Configured Agent instance.

    Example:
        >>> agent = create_agent(
        ...     name="Researcher",
        ...     instructions="Search the web and summarize findings.",
        ... )
        >>> result = agent("Search for Python 3.14 release notes.")
    """
    if tools is None:
        tools = [search_web]

    model = create_model()
    agent = Agent(
        model=model,
        tools=tools,
        system_prompt=instructions,
    )
    return agent


def create_researcher() -> Agent:
    """Create a Researcher agent with search and calculator tools.

    The Researcher uses web search to find information and the calculator
    for numerical operations. Returns structured summaries.

    Returns:
        Configured Researcher Agent.
    """
    return create_agent(
        name="Researcher",
        instructions=(
            "You are a researcher. Use web search to find information. "
            "Be thorough and factual. Return your findings as a structured "
            "summary with key points, dates, and relevant details."
        ),
        tools=[search_web, calculator],
    )


def create_writer() -> Agent:
    """Create a Writer agent for formatting reports.

    The Writer takes research findings and formats them into well-structured
    reports with headings, bullet points, and proper formatting.

    Returns:
        Configured Writer Agent.
    """
    return create_agent(
        name="Writer",
        instructions=(
            "You are a technical writer. Take the research provided and "
            "write a clear, well-structured report. Use headings, bullet "
            "points, and proper formatting. Be concise but comprehensive."
        ),
        tools=[write_file],
    )


def run_pipeline(topic: str) -> str:
    """Run Researcher → Writer pipeline.

    Strands has NO built-in orchestration. Multi-agent is manual composition:
    Agent A's output → Agent B's input (string passing).

    Args:
        topic: The research topic.

    Returns:
        The final formatted report.
    """
    print(f"\n{'=' * 60}")
    print(f"Strands Pipeline: Research → Write")
    print(f"Topic: {topic}")
    print(f"{'=' * 60}\n")

    # Step 1: Researcher searches and summarizes
    researcher = create_researcher()
    research_prompt = (
        f"Research the topic: {topic}. "
        f"Use web search to find recent information. "
        f"Return a structured summary with key findings."
    )
    print("[Researcher] Starting research...")
    research_result = researcher(research_prompt)
    print(f"\n[Researcher] Result:\n{research_result}\n")

    # Step 2: Writer takes research results and formats a report
    writer = create_writer()
    writing_prompt = (
        f"Based on the following research findings, write a well-structured report:\n\n"
        f"--- FINDINGS ---\n{research_result}\n--- END ---\n\n"
        f"Write a report with: Title, Introduction, Key Findings (bullet points), Conclusion."
    )
    print("[Writer] Starting report...")
    final_report = writer(writing_prompt)
    print(f"\n[Writer] Final Report:\n{final_report}\n")

    return str(final_report)
