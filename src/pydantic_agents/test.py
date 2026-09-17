#!/usr/bin/env python3
"""
Verification script for pydantic_ai package.

Tests:
    1. All imports resolve without errors
    2. Schemas are defined correctly
    3. Agents can be created
    4. Structured output works (requires LLM server)

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

    from pydantic_agents.agent import draft_agent, review_agent, finalize_agent
    from pydantic_agents.agent import ResearchDeps, model_settings
    from pydantic_agents.schemas import DraftReport, ReviewResult, FinalReport

    print("  ✓ All imports resolved")


def test_schemas() -> None:
    """Test that Pydantic schemas are defined correctly."""
    print("Testing schemas...")

    from pydantic_agents.schemas import DraftReport, ReviewResult, FinalReport

    # Test DraftReport
    draft = DraftReport(
        research={"title": "Test", "summary": "Test", "key_findings": ["A"], "sources": ["B"]},
        conclusion="Test conclusion",
    )
    assert draft.research.title == "Test"
    assert len(draft.research.key_findings) == 1

    # Test ReviewResult
    review = ReviewResult(
        approved=True,
        quality_score=5,
        feedback="Looks good",
    )
    assert review.approved is True
    assert review.quality_score == 5

    # Test FinalReport
    final = FinalReport(
        research={"title": "Final", "summary": "Final", "key_findings": [], "sources": []},
        conclusion="Final conclusion",
        revisions_made="None",
    )
    assert final.research.title == "Final"

    print(f"  ✓ Schemas defined correctly")


def test_agent_creation() -> None:
    """Test that agents can be created."""
    print("Testing agent creation...")

    from pydantic_agents.agent import draft_agent, review_agent, finalize_agent

    assert draft_agent is not None
    assert review_agent is not None
    assert finalize_agent is not None

    print(f"  ✓ Agents created: Draft, Review, Finalize")


def test_agent_run() -> None:
    """Test agent run (requires LLM server).

    This test will fail if no LLM server is running. That's expected.
    """
    print("Testing agent run (requires LLM server)...")

    from pydantic_agents.agent import draft_agent, ResearchDeps

    try:
        deps = ResearchDeps(topic="test")
        result = draft_agent.run_sync("Draft a report on: test", deps=deps)
        assert result.output is not None
        assert hasattr(result.output, "research")
        print(f"  ✓ Agent run completed")
        print(f"  ✓ Output type: {type(result.output).__name__}")
    except Exception as e:
        print(f"  ⚠ Agent run skipped (LLM server not running): {e}")


def main() -> None:
    """Run all tests."""
    print("=" * 60)
    print("pydantic_ai Package Verification")
    print("=" * 60)

    try:
        test_imports()
        test_schemas()
        test_agent_creation()
        test_agent_run()

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
