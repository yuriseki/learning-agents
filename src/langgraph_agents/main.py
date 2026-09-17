#!/usr/bin/env python3
"""
LangGraph — Entry Point.

Demonstrates StateGraph with conditional routing and feedback loops:
Research -> Draft -> Review -> (Revise) -> Finalize

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

from langgraph_agents.graph import build_graph


def run_pipeline(topic: str) -> dict:
    """Run the state graph pipeline with streaming output.

    Args:
        topic: The research topic.

    Returns:
        Final state dict with all accumulated data.
    """
    print(f"\n{'=' * 60}")
    print(f"LangGraph Pipeline: {topic}")
    print(f"{'=' * 60}\n")

    graph = build_graph()

    # Initial state
    initial_state = {
        "topic": topic,
        "research_results": "",
        "draft": "",
        "review_feedback": "",
        "final_output": "",
        "revision_count": 0,
    }

    # Config with checkpointer enables state persistence
    config = {"configurable": {"thread_id": "1"}}

    print("Running graph (streaming mode)...\n")

    # stream() yields events after each node executes
    final_state = initial_state
    for event in graph.stream(initial_state, config=config):
        for node_name, state_update in event.items():
            print(f"\n--- After node: {node_name} ---")
            for key, value in state_update.items():
                if isinstance(value, str):
                    preview = value[:150].replace('\n', ' ')
                    print(f"  {key}: {preview}...")
                else:
                    print(f"  {key}: {value}")
            final_state = {**final_state, **state_update}

    # Print the final output
    print(f"\n{'=' * 60}")
    print("FINAL OUTPUT:")
    print(f"{'=' * 60}\n")
    print(final_state.get("final_output", "No output produced"))

    return final_state


def main() -> None:
    """Run the pipeline."""
    topic = sys.argv[1] if len(sys.argv) > 1 else "Python 3.14 release"
    final_state = run_pipeline(topic)
    print(f"\nDone! Report length: {len(final_state.get('final_output', ''))} chars")


if __name__ == "__main__":
    main()
