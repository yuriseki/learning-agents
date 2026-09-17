#!/usr/bin/env python3
"""
AG2 (AutoGen) — Entry Point.

Usage:
    python3 main.py                    # Run with default topic
    python3 main.py "Your topic"       # Run with custom topic

Note: This package uses its own isolated venv at src/ag2_agents/.venv/
to avoid dependency conflicts with other frameworks.
"""

import sys
from agent import run_single_agent


def main() -> None:
    """Run the single agent research."""
    topic = sys.argv[1] if len(sys.argv) > 1 else "Python 3.14 release"
    result = run_single_agent(topic)
    print(f"\nDone!")


if __name__ == "__main__":
    main()
