"""
LangGraph — Stateful directed graphs with conditional routing.

LangGraph uses StateGraph with TypedDict state, conditional edges, and
feedback loops. It's the most complex framework but also the most powerful.

Key concepts:
    - State: TypedDict defining shared data between nodes
    - Nodes: Functions that read state and return partial updates
    - Edges: Fixed (A -> B) or conditional (A -> B or C based on state)
    - Checkpointing: MemorySaver for state persistence between nodes

Flow: START -> research -> draft -> review -> (revise -> review)* -> finalize -> END
"""

__all__ = []
