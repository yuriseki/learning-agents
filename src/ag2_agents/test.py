#!/usr/bin/env python3
"""Verification script for ag2_agents package."""

import sys
from pathlib import Path

# Add src/ to path for shared module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def test_imports() -> None:
    """Test that all imports resolve."""
    print("Testing imports...")
    from ag2_agents.agent import create_researcher, run_single_agent
    print("  ✓ All imports resolved")

def test_agent_creation() -> None:
    """Test that agent can be created."""
    print("Testing agent creation...")
    from ag2_agents.agent import create_researcher
    agent = create_researcher()
    assert agent is not None
    print("  ✓ Agent created")

def main() -> None:
    print("=" * 60)
    print("ag2_agents Package Verification")
    print("=" * 60)
    try:
        test_imports()
        test_agent_creation()
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"Test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
