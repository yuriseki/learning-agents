"""
Graph construction with conditional routing.

The graph defines:
1. Nodes (what work to do)
2. Edges (how they connect)
3. Conditional edges (decisions based on state)

Flow: START -> research -> draft -> review -> (revise -> review)* -> finalize -> END
"""

# Import framework BEFORE adding src/ to path (avoids shadowing)
import langgraph.graph as _lg_graph
StateGraph = _lg_graph.StateGraph
START = _lg_graph.START
END = _lg_graph.END
import langgraph.checkpoint.memory as _lg_memory
MemorySaver = _lg_memory.MemorySaver

import sys
from pathlib import Path

# Add src/ to path for shared module import
_SRC_ROOT = Path(__file__).resolve().parent.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from langgraph_agents.state import PipelineState
from langgraph_agents.nodes import (
    research_node, draft_node, review_node, revise_node, finalize_node
)


def should_revise(state: PipelineState) -> str:
    """Conditional routing: decide whether to revise or finalize.

    This function runs AFTER the Review node. It inspects the state
    (specifically the review_feedback) and returns a string that maps
    to a node name.

    Args:
        state: Current state (includes review_feedback from review_node)

    Returns:
        "finalize" if quality is approved, "revise" if needs improvement
    """
    feedback = state.get("review_feedback", "")
    revision_count = state.get("revision_count", 0)

    # Safety net: max 2 revisions (prevent infinite loops)
    if revision_count >= 2:
        print(f"\n[ROUTING] Max revisions reached ({revision_count}), forcing finalize")
        return "finalize"

    # Check if the review feedback starts with APPROVED
    if feedback.upper().startswith("APPROVED"):
        print(f"\n[ROUTING] Review approved -> go to finalize")
        return "finalize"
    else:
        print(f"\n[ROUTING] Review says revise -> go back to revise node")
        return "revise"


def build_graph():
    """Build the research -> draft -> review -> (revise -> review) -> finalize graph.

    Returns:
        Compiled StateGraph with checkpointing.
    """
    # Create the graph with the state schema
    builder = StateGraph(PipelineState)

    # Add nodes (name + function)
    builder.add_node("research", research_node)
    builder.add_node("draft", draft_node)
    builder.add_node("review", review_node)
    builder.add_node("revise", revise_node)
    builder.add_node("finalize", finalize_node)

    # Fixed edges (always go from A to B)
    builder.add_edge(START, "research")       # Entry point -> research
    builder.add_edge("research", "draft")     # research -> draft
    builder.add_edge("draft", "review")       # draft -> review

    # Conditional edge: Review -> Revise OR Finalize
    builder.add_conditional_edges(
        "review",
        should_revise,
        {
            "revise": "revise",
            "finalize": "finalize",
        }
    )

    # Revise -> Review (loop back for re-evaluation)
    builder.add_edge("revise", "review")

    # Finalize -> End
    builder.add_edge("finalize", END)

    # Compile with checkpoint (enables state persistence between nodes)
    checkpoint = MemorySaver()
    graph = builder.compile(checkpointer=checkpoint)

    return graph
