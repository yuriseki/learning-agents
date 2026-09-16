"""
SimpleAgent — A from-scratch ReAct agent with tool calling and message management.

This is the FOUNDATION that every agent framework builds on. Understanding this
code means you understand what frameworks like LangGraph, CrewAI, and AG2 actually
do under the hood.

Core concepts:
    - ReAct loop: Thought → Action → Observation → repeat
    - Tool calling: LLM decides which tools to use, we execute them
    - Message management: conversation history IS the agent's memory
    - Termination: LLM stops calling tools = done; max iterations = safety net
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
    """A minimal agent with a ReAct loop, tool calling, and message management.

    This agent maintains its own conversation history (list of messages) and
    loops until the LLM provides a final answer without tool calls.

    Termination conditions:
        - The LLM responds WITHOUT tool calls (gives a final answer)
        - Max iterations reached (safety net to prevent infinite loops)
        - LLM endpoint error (graceful degradation)

    Example:
        >>> agent = SimpleAgent(
        ...     name="Researcher",
        ...     instructions="Search the web and summarize findings.",
        ...     max_iterations=10,
        ... )
        >>> result = agent.run("Search for Python 3.14 release notes.")
        >>> print(result)
    """

    def __init__(
        self,
        name: str,
        instructions: str,
        max_iterations: int = 10,
    ) -> None:
        """Create a new agent.

        Args:
            name: Display name for logging (e.g., "Researcher").
            instructions: System prompt defining the agent's role and behavior.
            max_iterations: Safety net — max ReAct loop iterations before forced stop.
        """
        self.name = name
        self.instructions = instructions
        self.max_iterations = max_iterations
        self.messages: list[dict[str, Any]] = []  # Conversation history
        self.client = OpenAI(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
        )
        self._init_system_message()

    def _init_system_message(self) -> None:
        """Set up the system message with role instructions and tool awareness."""
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
        """Run the ReAct loop: thought → action → observation → repeat.

        Each iteration:
            1. Sends the full conversation + tool schemas to the LLM
            2. Checks if the LLM wants to call tools
            3. If yes: executes tools, adds results to conversation, repeats
            4. If no: returns the final answer

        Args:
            user_message: The task or question for the agent to solve.

        Returns:
            The agent's final answer (string), or a timeout/error message.
        """
        # Add user message to conversation history
        self.messages.append({"role": "user", "content": user_message})

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'=' * 60}")
            print(f"[{self.name}] Iteration {iteration}/{self.max_iterations}")

            # Step 1: Send conversation to the LLM with tool schemas
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=self.messages,
                    tools=TOOLS,
                    max_tokens=LLM_MAX_TOKENS,
                    extra_body=LLM_EXTRA_BODY,
                )
            except Exception as e:
                error_msg = f"ERROR connecting to LLM: {e}"
                print(f"[{self.name}] {error_msg}")
                return error_msg

            message = response.choices[0].message

            # Step 2: Check if the LLM wants to call a tool
            if message.tool_calls:
                # The LLM wants to use a tool — extract tool calls
                tool_names = [tc.function.name for tc in message.tool_calls]
                print(f"[{self.name}] Tool calls: {tool_names}")

                # Add the LLM's message to history (so it knows what it decided)
                self.messages.append(message.model_dump())

                # Step 3: Execute each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = self._parse_arguments(tool_call.function.arguments)

                    # Execute through the safe dispatcher (whitelist check)
                    result = safe_execute_tool(function_name, arguments)
                    display = result[:300] + "..." if len(result) > 300 else result
                    print(f"[{self.name}] Tool '{function_name}' result: {display}")

                    # Add tool result back to conversation as a "tool" role message
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    })

                # Continue the loop — LLM will reason about the tool results
                continue

            # Step 4: No tool calls — the LLM is giving its final answer
            print(f"[{self.name}] Final answer (no more tool calls)")
            return message.content or "(empty response)"

        # Max iterations reached without completion
        return f"[TIMEOUT] {self.name} did not complete within {self.max_iterations} iterations."

    @staticmethod
    def _parse_arguments(args_json: str) -> dict[str, Any]:
        """Parse JSON arguments from the LLM's tool call.

        Args:
            args_json: JSON string of arguments from the LLM.

        Returns:
            Dict of arguments, or empty dict if parsing fails.
        """
        try:
            return json.loads(args_json)
        except json.JSONDecodeError:
            print(f"[WARNING] Could not parse arguments: {args_json[:100]}")
            return {}


# =============================================================================
# Specialized Agents (for multi-agent pipelines)
# =============================================================================


class ResearcherAgent(SimpleAgent):
    """Specialized agent for research tasks. Uses web search to gather info."""

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
    """Specialized agent for writing reports. Takes research and formats it."""

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
    """Run Researcher → Writer pipeline (simple message passing).

    This demonstrates the fundamental multi-agent pattern:
        1. Researcher agent gathers information (uses tools)
        2. Researcher's output is passed as input to Writer
        3. Writer formats into a report (no tools needed, just formatting)

    This is the simplest form of multi-agent communication:
    Agent A's output → Agent B's input (just strings!)

    Args:
        topic: The research topic.

    Returns:
        The final formatted report.
    """
    print(f"\n{'#' * 60}")
    print(f"Multi-Agent Pipeline: Research → Write")
    print(f"Topic: {topic}")
    print(f"{'#' * 60}")

    # Step 1: Researcher gathers information
    research_prompt = (
        f"Research the topic: {topic}. "
        "Find key facts, recent developments, and relevant details. "
        "Search for multiple aspects of the topic."
    )
    print(f"\n--- Phase 1: Research ---")
    research_results = ResearcherAgent().run(research_prompt)

    # Step 2: Writer takes research results and produces a report
    # This IS the message passing — research_results (string) becomes writer input
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
