#!/usr/bin/env python3
"""
Pydantic AI — Entry Point.

Demonstrates structured output with validation-first design:
Draft -> Review -> (Revise) -> Finalize

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

from pydantic_agents.agent import draft_agent, review_agent, finalize_agent, ResearchDeps, model_settings
from pydantic_agents.schemas import DraftReport, ReviewResult, FinalReport


def run_pipeline(topic: str, max_revisions: int = 2) -> FinalReport:
    """Run the multi-step research pipeline.

    Args:
        topic: The research topic.
        max_revisions: Maximum revision iterations.

    Returns:
        FinalReport (Pydantic model).
    """
    deps = ResearchDeps(topic=topic)

    print(f"\n{'=' * 60}")
    print(f"Pydantic AI Pipeline: {topic}")
    print(f"{'=' * 60}\n")

    # Step 1: Draft
    print("[DRAFT] Writing initial draft...")
    draft_result = draft_agent.run_sync(f"Draft a report on: {topic}", deps=deps)
    draft = draft_result.output  # type: DraftReport

    print(f"  Draft title: {draft.research.title}")
    print(f"  Findings: {len(draft.research.key_findings)} items")
    print(f"  Tokens: {draft_result.usage}")

    # Step 2: Review (with revision loop)
    for revision in range(max_revisions):
        print(f"\n[REVIEW] Reviewing draft (pass {revision + 1})...")

        review_prompt = f"Review this draft report:\n\n{draft.model_dump_json(indent=2)}"
        review_result = review_agent.run_sync(review_prompt, deps=deps)
        review = review_result.output  # type: ReviewResult

        print(f"  Approved: {review.approved}")
        print(f"  Quality: {review.quality_score}/5")
        print(f"  Feedback: {review.feedback[:150]}...")

        if review.approved:
            print("\n✓ Draft approved — moving to finalize")
            break

        # Revise
        print(f"\n[REVISE] Improving draft (revision {revision + 1})...")
        revise_prompt = (
            f"Improve this draft based on review feedback:\n\n"
            f"--- DRAFT ---\n{draft.model_dump_json(indent=2)}\n"
            f"--- FEEDBACK ---\n{review.feedback}\n"
            f"--- END ---\n\n"
            f"Produce an improved draft."
        )
        revised_result = draft_agent.run_sync(revise_prompt, deps=deps)
        draft = revised_result.output
        print(f"  Revised title: {draft.research.title}")

    # Step 3: Finalize
    print(f"\n[FINALIZE] Producing final report...")
    finalize_prompt = (
        f"Finalize this report based on the review:\n\n"
        f"--- DRAFT ---\n{draft.model_dump_json(indent=2)}\n"
        f"--- REVIEW ---\n{review.feedback}\n"
        f"--- END ---\n\n"
        f"Produce the final polished report."
    )
    final_result = finalize_agent.run_sync(finalize_prompt, deps=deps)
    final = final_result.output  # type: FinalReport

    # Output
    print(f"\n{'=' * 60}")
    print("FINAL REPORT:")
    print(f"{'=' * 60}\n")
    print(f"Title: {final.research.title}")
    print(f"Summary: {final.research.summary}")
    print(f"Findings: {len(final.research.key_findings)} items")
    print(f"Conclusion: {final.conclusion}")

    return final


def main() -> None:
    """Run the pipeline."""
    topic = sys.argv[1] if len(sys.argv) > 1 else "Python 3.14 release"
    final = run_pipeline(topic)
    print(f"\nDone! Report: {len(final.research.summary)} chars")


if __name__ == "__main__":
    main()
