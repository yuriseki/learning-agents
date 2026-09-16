"""
From-Scratch ReAct Agent

A minimal agent built without any framework. Implements the core patterns
that every agent framework abstracts: ReAct loops, tool calling, message
management, and termination conditions.

The ReAct loop (Reasoning + Acting):
    1. Send conversation history + tool schemas to the LLM
    2. LLM responds with either tool calls OR a final answer
    3. If tool calls: execute them, feed results back, repeat from step 1
    4. If final answer: return it and stop

Usage:
    python3 -m from_scratch
    # or
    cd src/from_scratch && python3 main.py
"""

from from_scratch.agent import SimpleAgent
from from_scratch.tools import TOOLS, TOOL_FUNCTIONS

__all__ = ["SimpleAgent", "TOOLS", "TOOL_FUNCTIONS"]
