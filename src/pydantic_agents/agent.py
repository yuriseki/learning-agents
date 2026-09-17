"""
Agent definitions for Pydantic AI.

Three agents:
1. Draft Agent — produces a DraftReport (ResearchResult + conclusion)
2. Review Agent — produces a ReviewResult (approved + feedback)
3. Finalize Agent — produces a FinalReport (after revision)

All agents use dependency injection (RunContext) and shared model config.
"""

# Import framework BEFORE adding src/ to path (avoids shadowing)
import pydantic_ai as _pydantic_ai
Agent = _pydantic_ai.Agent
RunContext = _pydantic_ai.RunContext
import pydantic_ai.models.openai as _pai_openai
OpenAIChatModel = _pai_openai.OpenAIChatModel
import pydantic_ai.providers.openai as _pai_provider
OpenAIProvider = _pai_provider.OpenAIProvider

import sys
from dataclasses import dataclass
from pathlib import Path

from ddgs import DDGS
from openai import AsyncOpenAI

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
from pydantic_agents.schemas import DraftReport, ReviewResult, FinalReport


# Shared model configuration — connects to llama.cpp
client = AsyncOpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
provider = OpenAIProvider(openai_client=client)
model = OpenAIChatModel(LLM_MODEL, provider=provider)


# ─────────────────────────────────────────────
# Dependency Injection
# ─────────────────────────────────────────────
@dataclass
class ResearchDeps:
    """Dependencies injected into all agents."""
    topic: str = ""


# ─────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────
async def search_web(ctx: RunContext[ResearchDeps], query: str) -> str:
    """Search the web using DuckDuckGo. Takes a search query and returns results."""
    print(f"  [TOOL] Searching web for: {query}")
    try:
        results = DDGS().text(query, max_results=5)
        formatted = "\n\n".join(
            f"[{i+1}] {r['title']}: {r['body']}" for i, r in enumerate(results)
        )
        return formatted if formatted else "No results found."
    except Exception as e:
        return f"Search error: {e}"


# ─────────────────────────────────────────────
# Model Settings
# ─────────────────────────────────────────────
model_settings = {
    "temperature": LLM_TEMPERATURE,
    "max_tokens": 4096,
    "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
}


# ─────────────────────────────────────────────
# Draft Agent
# ─────────────────────────────────────────────
draft_agent = Agent(
    model,
    deps_type=ResearchDeps,
    output_type=DraftReport,
    model_settings=model_settings,
    instructions=(
        "You are a research agent. Research the given topic and produce a structured draft report.\n"
        "Use the search_web tool to find current information.\n"
        "The draft must include research findings (title, summary, key findings, sources) and a conclusion."
    ),
)
draft_agent.tool(search_web)


# ─────────────────────────────────────────────
# Review Agent
# ─────────────────────────────────────────────
review_agent = Agent(
    model,
    deps_type=ResearchDeps,
    output_type=ReviewResult,
    model_settings=model_settings,
    instructions=(
        "You are a quality review agent. Review the draft report for:\n"
        "1. Accuracy: Are facts clear and consistent?\n"
        "2. Structure: Is it well-organized?\n"
        "3. Completeness: Does it cover the key points?\n\n"
        "If quality is good (score >= 4), set approved=True.\n"
        "If quality needs improvement (score < 4), set approved=False and provide specific feedback."
    ),
)


# ─────────────────────────────────────────────
# Finalize Agent
# ─────────────────────────────────────────────
finalize_agent = Agent(
    model,
    deps_type=ResearchDeps,
    output_type=FinalReport,
    model_settings=model_settings,
    instructions=(
        "You are a finalization agent. Polish the draft based on review feedback.\n"
        "Produce a FinalReport with:\n"
        "- Research findings (may be improved based on feedback)\n"
        "- A polished conclusion\n"
        "- A summary of what was revised"
    ),
)
