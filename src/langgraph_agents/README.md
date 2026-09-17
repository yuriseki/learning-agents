# LangGraph

Stateful directed graphs with conditional routing and feedback loops. Most complex, most powerful.

## Quick Start

```bash
# Install shared dependencies
pip install -r ../shared/requirements.txt

# Install LangGraph dependencies
pip install -r requirements.txt

# Run the pipeline
python3 main.py                    # Default topic
python3 main.py "Python 3.14"     # Custom topic

# Run tests
python3 test.py
```

## The State Graph Pattern

Define state, nodes, edges, and conditional routing:

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

# 1. Define state
class PipelineState(TypedDict):
    topic: str
    research_results: str
    draft: str
    review_feedback: str
    final_output: str
    revision_count: int

# 2. Build the graph
builder = StateGraph(PipelineState)
builder.add_node("research", research_node)
builder.add_node("draft", draft_node)
builder.add_node("review", review_node)
builder.add_node("revise", revise_node)
builder.add_node("finalize", finalize_node)

# 3. Fixed edges
builder.add_edge(START, "research")
builder.add_edge("research", "draft")
builder.add_edge("draft", "review")

# 4. Conditional edge (routing function)
builder.add_conditional_edges(
    "review",
    should_revise,  # Returns "revise" or "finalize"
    {"revise": "revise", "finalize": "finalize"},
)

# 5. Feedback loop
builder.add_edge("revise", "review")
builder.add_edge("finalize", END)

# 6. Compile with checkpointing
graph = builder.compile(checkpointer=MemorySaver())
```

## Conditional Routing

The routing function decides where to go next:

```python
def should_revise(state: PipelineState) -> str:
    feedback = state.get("review_feedback", "")
    revision_count = state.get("revision_count", 0)

    # Safety net: max 2 revisions
    if revision_count >= 2:
        return "finalize"

    if feedback.upper().startswith("APPROVED"):
        return "finalize"
    else:
        return "revise"
```

## Streaming

Use `stream()` to see each node's output:

```python
for event in graph.stream(initial_state, config=config):
    for node_name, state_update in event.items():
        print(f"After {node_name}: {state_update}")
```

## Known Issues

- **langchain-openai required**: NOT langchain-ollama. Use `ChatOpenAI(base_url=...)`.
- **State is TypedDict**: Nodes return partial updates, LangGraph merges.
- **MemorySaver for checkpointing**: Enables state persistence between nodes.
- **extra_body for thinking**: `extra_body={"enable_thinking": False}` needed for reasoning models.

## Comparison

| Aspect | CrewAI | AG2 | LangGraph |
|--------|--------|-----|-----------|
| Orchestration | Sequential tasks | Conversation loop | **State graph** |
| Feedback loop | No | Yes (debate) | **Yes (revision)** |
| State | Task context | Shared history | **TypedDict** |
| Routing | Fixed | Fixed | **Conditional** |
| Persistence | No | No | **MemorySaver** |
| Complexity | Low | Medium | **High** |

## Requirements

- Python 3.10+
- `langgraph` — LangGraph framework
- `langchain-openai` — OpenAI-compatible API client
- `langchain-core` — Core abstractions
- `langgraph-checkpoint-memory` — Memory checkpointing
- `ddgs` — DuckDuckGo search (from shared)
