#!/usr/bin/env python3
"""
From-Scratch ReAct Agent — Entry Point

Demonstrates:
    1. Single agent with tool calling (ReAct loop)
    2. Multi-agent pipeline (Researcher → Writer)

Usage:
    python3 main.py                    # Run with default topic
    python3 main.py "Your topic here"  # Run with custom topic
"""

import sys
from pathlib import Path

# Add src/ to path for shared module import
_SRC_ROOT = Path(__file__).resolve().parent.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from from_scratch.agent import SimpleAgent, run_multi_agent_pipeline


def main() -> None:
    """Run single agent test and multi-agent pipeline."""
    topic = sys.argv[1] if len(sys.argv) > 1 else "Python 3.14 release"

    # ─────────────────────────────────────────────
    # Part 1: Single Agent Test
    # ─────────────────────────────────────────────
    print("=" * 60)
    print("Part 1: Single Agent Test")
    print("=" * 60)

    agent = SimpleAgent(
        name="Assistant",
        instructions=(
            "You are a helpful assistant. Use web search to find "
            "current information when needed. Be concise and factual."
        ),
        max_iterations=5,
    )

    result = agent.run(
        f"Search for the latest information about {topic}. "
        "Summarize the key findings in 3-5 bullet points."
    )
    print(f"\n--- Single Agent Result ---\n{result}")

    # ─────────────────────────────────────────────
    # Part 2: Multi-Agent Pipeline
    # ─────────────────────────────────────────────
    print("\n\n")
    report = run_multi_agent_pipeline(topic)
    print(f"\n--- Final Report ---\n{report}")


if __name__ == "__main__":
    main()
