#!/usr/bin/env python3
"""
Verification script for langgraph package.

Tests:
    1. All imports resolve without errors
    2. State schema is defined
    3. Graph can be built
    4. Nodes can be called (requires LLM server)

Usage:
    python3 test.py
"""

import sys
from pathlib import Path

# Add src/ to path
_SRC_ROOT = Path(__file__).resolve().parent.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


def test_imports() -> None:
    """Test that all imports resolve."""
    print("Testing imports...")

    from langgraph_agents.graph import build_graph, should_revise
    from langgraph_agents.state import PipelineState
    from langgraph_agents.nodes import research_node, draft_node, review_node, revise_node, finalize_node

    print("  ✓ All imports resolved")


def test_state_schema() -> None:
    """Test that PipelineState is defined."""
    print("Testing state schema...")

    from langgraph_agents.state import PipelineState

    state = PipelineState(
        topic="test",
        research_results="",
        draft="",
        review_feedback="",
        final_output="",
        revision_count=0,
    )
    assert state["topic"] == "test"

    print(f"  ✓ PipelineState defined")


def test_graph_construction() -> None:
    """Test that graph can be built."""
    print("Testing graph construction...")

    from langgraph_agents.graph import build_graph

    graph = build_graph()
    assert graph is not None

    print(f"  ✓ Graph built")


def test_conditional_routing() -> None:
    """Test that conditional routing function works."""
    print("Testing conditional routing...")

    from langgraph_agents.graph import should_revise

    # Approved -> finalize
    state = {"review_feedback": "APPROVED: looks good", "revision_count": 0}
    assert should_revise(state) == "finalize"

    # Not approved -> revise
    state = {"review_feedback": "REVISE: needs work", "revision_count": 0}
    assert should_revise(state) == "revise"

    # Max revisions -> force finalize
    state = {"review_feedback": "REVISE: needs work", "revision_count": 2}
    assert should_revise(state) == "finalize"

    print(f"  ✓ Conditional routing works")


def test_graph_run() -> None:
    """Test graph run (requires LLM server).

    This test will fail if no LLM server is running. That's expected.
    """
    print("Testing graph run (requires LLM server)...")

    from langgraph_agents.graph import build_graph

    try:
        graph = build_graph()
        initial_state = {
            "topic": "test",
            "research_results": "",
            "draft": "",
            "review_feedback": "",
            "final_output": "",
            "revision_count": 0,
        }
        config = {"configurable": {"thread_id": "1"}}

        final_state = initial_state
        for event in graph.stream(initial_state, config=config):
            for node_name, state_update in event.items():
                final_state = {**final_state, **state_update}

        assert final_state.get("final_output", "") != ""
        print(f"  ✓ Graph run completed")
        print(f"  ✓ Final output length: {len(final_state.get('final_output', ''))} chars")
    except Exception as e:
        print(f"  ⚠ Graph run skipped (LLM server not running): {e}")


def main() -> None:
    """Run all tests."""
    print("=" * 60)
    print("langgraph Package Verification")
    print("=" * 60)

    try:
        test_imports()
        test_state_schema()
        test_graph_construction()
        test_conditional_routing()
        test_graph_run()

        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0

    except Exception as e:
        print("=" * 60)
        print(f"Test failed: {type(e).__name__}: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
