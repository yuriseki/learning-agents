"""
Strands Agents — 3 Primitives, Maximum Clarity.

Strands Agents (AWS) is the simplest framework in the series. Three primitives:
    1. Model — the LLM connection (OpenAI-compatible API)
    2. Tools — @tool decorated functions (auto-extract JSON schemas)
    3. Agent — runs the ReAct loop internally (model-driven)

Unlike from-scratch, you don't write the ReAct loop. Strands handles it.
The model drives the loop — it decides when to call tools and when to stop.

Usage:
    python3 -m strands_agents
    # or
    cd src/strands_agents && python3 main.py
"""

from strands_agents.agent import create_agent, create_researcher, create_writer
from strands_agents.tools import search_web, read_file, write_file

__all__ = [
    "create_agent",
    "create_researcher",
    "create_writer",
    "search_web",
    "read_file",
    "write_file",
]
