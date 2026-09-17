#!/usr/bin/env python3
"""
Smolagents — Entry Point.

Demonstrates the code-as-tool pattern: the agent writes and executes
Python code instead of making JSON tool calls.

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

from smol_agents.agent import run_pipeline


def main() -> None:
    """Run the Researcher -> Writer pipeline."""
    topic = sys.argv[1] if len(sys.argv) > 1 else "Python 3.14 release"
    report = run_pipeline(topic)
    print(f"\nDone! Report length: {len(report)} chars")


if __name__ == "__main__":
    main()
