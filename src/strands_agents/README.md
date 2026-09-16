# Strands Agents

Three primitives, maximum clarity. Strands Agents (AWS) is the simplest framework in the series.

## Quick Start

```bash
# Install shared dependencies
pip install -r ../shared/requirements.txt

# Install Strands dependencies
pip install -r requirements.txt

# Run the agent
python3 main.py                    # Default topic
python3 main.py "Python 3.14"     # Custom topic

# Run tests
python3 test.py
```

## The 3 Primitives

### 1. Model

Connects to the LLM via OpenAI-compatible API:

```python
from strands.models.openai import OpenAIModel

model = OpenAIModel(
    client_args={"api_key": "not-needed", "base_url": "http://localhost:8124/v1"},
    model_id="Qwen3.6-27B",
    params={"max_tokens": 1024, "temperature": 0.7},
)
```

### 2. Tools

`@tool` decorated functions. The decorator auto-extracts JSON schemas:

```python
from strands import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # implementation
```

No manual JSON schemas. No dispatch maps. No whitelists.

### 3. Agent

Runs the ReAct loop internally:

```python
from strands import Agent

agent = Agent(model=model, tools=[search_web])
result = agent("Search for Python 3.14")
```

You don't write the loop. Strands handles it.

## Model-Driven Design

The model decides when to call tools and when to stop. This means:

- **Less code**: No manual ReAct loop to write
- **Less control**: You can't intercept the loop between iterations
- **Model quality matters**: A better model = a better agent

Compare to from-scratch:

| Aspect | From-Scratch | Strands |
|--------|-------------|---------|
| ReAct loop | Hand-written `for` loop | Built into Agent |
| Tool definition | Manual JSON schemas | `@tool` decorator |
| Iteration control | `max_iterations` param | Not exposed (model-driven) |
| Observability | None | AgentResult (traces, metrics) |
| Lines of code | ~200 | ~80 |

## Multi-Agent Pipeline

Strands has NO built-in orchestration. Multi-agent is manual composition:

```python
# Agent A → Agent B (string passing)
research = researcher("Research: Python 3.14")
report = writer(f"Write a report based on: {research}")
```

## Configuration

Set environment variables (see `../shared/README.md`):

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BASE_URL` | `http://localhost:8124/v1` | LLM endpoint |
| `LLM_MODEL` | `Qwen3.6-27B` | Model name |
| `LLM_API_KEY` | `not-needed` | API key |

## Known Issues

- **Model-driven loop**: No `max_iterations` exposed. The model decides when to stop. If the model loops on search, you need to interrupt manually.
- **No built-in orchestration**: Multi-agent is manual string passing. For complex workflows, consider LangGraph.
- **Search rate limits**: DuckDuckGo may rate-limit from Docker sandboxes.

## Requirements

- Python 3.10+
- `strands-agents` — Strands Agents framework
- `strands-agents-tools` — Built-in tools (calculator, etc.)
- `openai` — OpenAI-compatible API client (from shared)
- `ddgs` — DuckDuckGo search (from shared)
