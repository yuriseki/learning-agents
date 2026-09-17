#!/usr/bin/env python3
"""
CrewAI — Entry Point.

Demonstrates role-based agent design, task handoff via context,
and Crew orchestration (crew.kickoff()).

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

import crewai as _crewai
Crew = _crewai.Crew
from crewai_agents.tasks import create_tasks


def run_crew(topic: str) -> str:
    """Run the crew with the research -> write -> review pipeline.

    Args:
        topic: The research topic.

    Returns:
        The final output from the crew.
    """
    print(f"\n{'=' * 60}")
    print(f"CrewAI Pipeline: Research -> Write -> Review")
    print(f"Topic: {topic}")
    print(f"{'=' * 60}\n")

    tasks = create_tasks(topic)

    # Create the crew and kick it off
    crew = Crew(
        agents=[task.agent for task in tasks],  # Extract agents from tasks
        tasks=tasks,
        verbose=True,
    )

    # kickoff() runs the entire pipeline sequentially
    # Returns AgentAction with all task outputs
    result = crew.kickoff()

    # Print each task's output
    if hasattr(result, 'tasks_output'):
        # Task 1 = Research+Write (the actual report)
        print(f"\n{'=' * 60}")
        print("WRITER'S REPORT (Task 1):")
        print(f"{'=' * 60}")
        print(str(result.tasks_output[0]))

        # Task 2 = Review (feedback on the report)
        print(f"\n{'=' * 60}")
        print("REVIEWER'S FEEDBACK (Task 2):")
        print(f"{'=' * 60}")
        print(str(result.tasks_output[1]))
    else:
        # Fallback: just print the final result
        print(result)

    return str(result)


def main() -> None:
    """Run the crew pipeline."""
    topic = sys.argv[1] if len(sys.argv) > 1 else "Python 3.14 release"
    report = run_crew(topic)
    print(f"\n{'=' * 60}")
    print(f"Done! Report length: {len(report)} chars")


if __name__ == "__main__":
    main()
