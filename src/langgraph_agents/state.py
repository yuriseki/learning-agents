"""
State schema for the LangGraph research pipeline.

The State is a TypedDict that defines what data all nodes can access.
Each node reads the state, does work, and returns a PARTIAL UPDATE
(only what changed). LangGraph merges these updates automatically.
"""

from typing_extensions import TypedDict


class PipelineState(TypedDict):
    """Shared state for the research -> draft -> review -> (revise) -> finalize pipeline."""

    # Input: the topic to research
    topic: str

    # Output from research node
    research_results: str

    # Output from draft node (updated by revise node)
    draft: str

    # Output from review node
    review_feedback: str

    # Output from finalize node
    final_output: str

    # Counter: how many revision loops have occurred (prevents infinite loops)
    revision_count: int
