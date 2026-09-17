#!/usr/bin/env python3
"""
Presentation Demo Script — From-Scratch ReAct Agent

This is agent.py with 5 pdb breakpoints for live debugging during presentation.
Each breakpoint is numbered and has a description of what to inspect.

Usage:
    python3 demo_breakpoints.py "Python 3.14 release"

At each breakpoint, use:
    <expression>  — inspect a variable
    c             — continue to next breakpoint
    q             — quit (if demo is done)
"""

import json
import sys
from pathlib import Path
from typing import Any

from openai import OpenAI

# Add src/ to path for shared module import
_SRC_ROOT = Path(__file__).resolve().parent.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from shared.config import (
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_API_KEY,
    LLM_MAX_TOKENS,
    LLM_EXTRA_BODY,
)
from from_scratch.tools import TOOLS, TOOL_FUNCTIONS, safe_execute_tool


class SimpleAgent:
    """Same as agent.py — with presentation breakpoints."""

    def __init__(
        self, name: str, instructions: str, max_iterations: int = 10
    ) -> None:
        self.name = name
        self.instructions = instructions
        self.max_iterations = max_iterations
        self.messages: list[dict[str, Any]] = []
        self.client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
        self._init_system_message()

    def _init_system_message(self) -> None:
        self.messages.append({
            "role": "system",
            "content": (
                f"You are {self.name}. {self.instructions}\n\n"
                "You have access to tools. If you need to use a tool to gather "
                "information, make a tool call. When you have enough information "
                "or your task is complete, respond with your final answer WITHOUT "
                "calling any more tools."
            ),
        })

    def run(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'=' * 60}")
            print(f"[{self.name}] Iteration {iteration}/{self.max_iterations}")

            # ─────────────────────────────────────────────────
            # BREAKPOINT 1: ReAct Loop Entry
            # Show: self.messages (agent memory), self.max_iterations
            # Narrate: "This for loop IS the agent. self.messages is its memory."
            # ─────────────────────────────────────────────────
            if iteration == 1:
                print("\n>>> BREAKPOINT 1: ReAct Loop Entry")
                print("    Inspect: self.name, self.max_iterations, self.messages")
                print("    Type 'c' to continue\n")
                import pdb; pdb.set_trace()

            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=self.messages,
                    tools=TOOLS,
                    max_tokens=LLM_MAX_TOKENS,
                    extra_body=LLM_EXTRA_BODY,
                )
            except Exception as e:
                print(f"[{self.name}] ERROR connecting to LLM: {e}")
                return f"ERROR: {e}"

            message = response.choices[0].message

            # ─────────────────────────────────────────────────
            # BREAKPOINT 2: First Tool Call
            # Show: message.tool_calls, tool name, arguments (JSON)
            # Narrate: "The LLM responded with JSON tool calls. It doesn't know Python."
            # ─────────────────────────────────────────────────
            if iteration == 1 and message.tool_calls:
                print("\n>>> BREAKPOINT 2: First Tool Call")
                print("    Inspect: message.tool_calls[0].function.name")
                print("    Inspect: message.tool_calls[0].function.arguments")
                print("    Type 'c' to continue\n")
                import pdb; pdb.set_trace()

            if message.tool_calls:
                tool_names = [tc.function.name for tc in message.tool_calls]
                print(f"[{self.name}] Tool calls: {tool_names}")
                self.messages.append(message.model_dump())

                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = self._parse_arguments(tool_call.function.arguments)
                    result = safe_execute_tool(function_name, arguments)
                    display = result[:300] + "..." if len(result) > 300 else result
                    print(f"[{self.name}] Tool '{function_name}' result: {display}")

                    # ─────────────────────────────────────────────────
                    # BREAKPOINT 3: Tool Execution Result
                    # Show: function_name, arguments, result, len(self.messages)
                    # Narrate: "Tool executed. Result added back to messages."
                    # ─────────────────────────────────────────────────
                    if iteration == 1:
                        print("\n>>> BREAKPOINT 3: Tool Result")
                        print("    Inspect: function_name, arguments, result[:200]")
                        print("    Inspect: len(self.messages)")
                        print("    Type 'c' to continue\n")
                        import pdb; pdb.set_trace()

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    })

                continue

            # ─────────────────────────────────────────────────
            # BREAKPOINT 4: Final Answer (no tool calls)
            # Show: message.tool_calls (None), message.content, iteration
            # Narrate: "No tool calls = LLM decided it's done."
            # ─────────────────────────────────────────────────
            print("\n>>> BREAKPOINT 4: Final Answer")
            print("    Inspect: message.tool_calls (should be None/empty)")
            print("    Inspect: message.content[:200]")
            print("    Inspect: iteration")
            print("    Type 'c' to continue\n")
            import pdb; pdb.set_trace()

            print(f"[{self.name}] Final answer (no more tool calls)")
            return message.content or "(empty response)"

        return f"[TIMEOUT] {self.name} did not complete within {self.max_iterations} iterations."

    @staticmethod
    def _parse_arguments(args_json: str) -> dict[str, Any]:
        try:
            return json.loads(args_json)
        except json.JSONDecodeError:
            return {}


class ResearcherAgent(SimpleAgent):
    def __init__(self, max_iterations: int = 10) -> None:
        super().__init__(
            name="Researcher",
            instructions=(
                "You are a researcher. Use web search to find information. "
                "Be thorough and factual. Return your findings as a structured "
                "summary with key points, dates, and relevant details."
            ),
            max_iterations=max_iterations,
        )


class WriterAgent(SimpleAgent):
    def __init__(self, max_iterations: int = 5) -> None:
        super().__init__(
            name="Writer",
            instructions=(
                "You are a technical writer. Take the research provided and "
                "write a clear, well-structured report. Use headings, bullet "
                "points, and proper formatting. Be concise but comprehensive."
            ),
            max_iterations=max_iterations,
        )


def run_multi_agent_pipeline(topic: str) -> str:
    print(f"\n{'#' * 60}")
    print(f"Multi-Agent Pipeline: Research → Write")
    print(f"Topic: {topic}")
    print(f"{'#' * 60}")

    research_prompt = (
        f"Research the topic: {topic}. "
        "Find key facts, recent developments, and relevant details. "
        "Search for multiple aspects of the topic."
    )
    print(f"\n--- Phase 1: Research ---")
    research_results = ResearcherAgent().run(research_prompt)

    # ─────────────────────────────────────────────────
    # BREAKPOINT 5: Multi-Agent String Passing
    # Show: research_results[:200], len(research_results)
    # Narrate: "Researcher done. String → Writer. This IS multi-agent."
    # ─────────────────────────────────────────────────
    print("\n>>> BREAKPOINT 5: Multi-Agent Handoff")
    print("    Inspect: research_results[:200]")
    print("    Inspect: len(research_results)")
    print("    Narrate: Researcher output → Writer input. This IS multi-agent.")
    print("    Type 'c' to continue\n")
    import pdb; pdb.set_trace()

    writing_prompt = (
        f"Based on the following research findings, write a comprehensive "
        f"report about '{topic}':\n\n"
        f"--- RESEARCH FINDINGS ---\n{research_results}\n"
        f"--- END FINDINGS ---\n\n"
        f"Write a well-structured report with an introduction, "
        f"key findings (with bullet points), and a conclusion."
    )
    print(f"\n--- Phase 2: Writing ---")
    final_report = WriterAgent().run(writing_prompt)

    return final_report


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "Python 3.14 release"
    print(f"Presentation Demo — Topic: {topic}\n")

    # Run single agent first (hits breakpoints 1-4)
    print("=" * 60)
    print("Part 1: Single Agent")
    print("=" * 60)
    agent = SimpleAgent(
        name="Assistant",
        instructions="You are a helpful assistant. Use web search when needed. Be concise.",
        max_iterations=5,
    )
    result = agent.run(
        f"Search for {topic}. Summarize key findings in 3-5 bullet points."
    )
    print(f"\n--- Result ---\n{result[:500]}...\n")

    # Run multi-agent (hits breakpoint 5)
    print("\n\n")
    report = run_multi_agent_pipeline(topic)
    print(f"\n--- Final Report ---\n{report[:500]}...\n")
