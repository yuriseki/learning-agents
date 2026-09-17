"""
Agent definitions with distinct personas and dual safety net.

In CrewAI, each Agent has:
    - role: Job title (becomes part of system prompt)
    - goal: What it's trying to achieve
    - backstory: Context/personality (shapes behavior)
    - max_iter: Max iterations before forcing answer (UNRELIABLE with local models)
    - max_execution_time: Hard timeout in seconds (RELIABLE safety net)

CRITICAL: Safety net lives on the Agent constructor, NOT the Task.
Always use BOTH max_iter AND max_execution_time with local models.
"""

# Import framework BEFORE adding src/ to path (avoids shadowing)
import os
os.environ.setdefault("OPENAI_API_KEY", "not-needed")

import crewai as _crewai
Agent = _crewai.Agent
Crew = _crewai.Crew
Task = _crewai.Task
LLM = _crewai.LLM

# Use a simple DuckDuckGo search tool instead of WebsiteSearchTool
# WebsiteSearchTool requires OpenAI API key, which we don't have for local models
from crewai.tools import BaseTool

class DuckDuckGoSearchTool(BaseTool):
    """Search the web using DuckDuckGo."""
    name: str = "Search the web"
    description: str = "Search the web using DuckDuckGo. Takes a search query and returns results."

    def _run(self, query: str) -> str:
        from ddgs import DDGS
        try:
            results = DDGS().text(query, max_results=5)
            formatted = "\n\n".join(
                f"[{i+1}] {r['title']}: {r['body']}" for i, r in enumerate(results)
            )
            return formatted if formatted else "No results found."
        except Exception as e:
            return f"Search error: {e}"

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
)


def create_llm():
    """Create shared LLM pointing to llama.cpp.

    Returns:
        Configured CrewAI LLM instance.
    """
    return LLM(
        model=LLM_MODEL,
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        temperature=LLM_TEMPERATURE,
    )


def create_researcher():
    """Create a Researcher agent with web search tools.

    Has web search tool. Dual safety net prevents endless looping.

    Returns:
        Configured Researcher Agent.
    """
    return Agent(
        role="Senior Research Analyst",
        goal=(
            "Find accurate, up-to-date information on the assigned topic. "
            "Thoroughly research using web search and return comprehensive findings."
        ),
        backstory=(
            "You are a meticulous researcher with 15 years of experience. "
            "You verify facts from multiple sources and present findings clearly. "
            "You always cite your sources."
        ),
        tools=[DuckDuckGoSearchTool()],
        llm=create_llm(),
        max_iter=30,
        max_execution_time=600,   # 5 minutes for research + writing
        verbose=True,
    )


def create_writer():
    """Create a Writer agent for formatting reports.

    No external tools needed — just formats text.

    Returns:
        Configured Writer Agent.
    """
    return Agent(
        role="Technical Writer",
        goal=(
            "Transform research findings into clear, well-structured reports. "
            "Use headings, bullet points, and proper formatting."
        ),
        backstory=(
            "You are a technical writer who specializes in making complex "
            "information accessible. You write in a professional tone with "
            "clear structure and actionable insights."
        ),
        tools=[],
        llm=create_llm(),
        max_iter=10,
        max_execution_time=600,
        verbose=True,
    )


def create_reviewer():
    """Create a Reviewer agent for quality evaluation.

    No tools — just reads and evaluates the draft.

    Returns:
        Configured Reviewer Agent.
    """
    return Agent(
        role="Quality Assurance Editor",
        goal=(
            "Review written content for accuracy, clarity, completeness, "
            "and proper formatting. Identify issues and suggest specific improvements."
        ),
        backstory=(
            "You are a senior editor with an eye for detail. You ensure all "
            "content meets professional standards. You provide constructive "
            "feedback with specific, actionable suggestions."
        ),
        tools=[],
        llm=create_llm(),
        max_iter=10,
        max_execution_time=600,
        verbose=True,
    )
