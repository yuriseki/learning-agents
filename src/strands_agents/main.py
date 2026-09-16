#!/usr/bin/env python3
"""
Strands Agents — Entry Point.

Demonstrates the 3-primitive architecture:
    1. Model (OpenAIModel → llama.cpp)
    2. Tools (@tool decorated functions)
    3. Agent (runs the ReAct loop internally)

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

from strands_agents.agent import run_pipeline


def main() -> None:
    """Run the Researcher → Writer pipeline."""
    topic = sys.argv[1] if len(sys.argv) > 1 else "Python 3.14 release"
    report = run_pipeline(topic)
    print(f"\nDone! Report length: {len(report)} chars")


if __name__ == "__main__":
    main()
