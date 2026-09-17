# Pydantic AI

Type-safe structured agents with validation-first design. The LLM MUST produce data matching the schema.

## Quick Start

```bash
# Install shared dependencies
pip install -r ../shared/requirements.txt

# Install Pydantic AI dependencies
pip install -r requirements.txt

# Run the pipeline
python3 main.py                    # Default topic
python3 main.py "Python 3.14"     # Custom topic

# Run tests
python3 test.py
```

## The Validation-First Design

Define Pydantic models as output contracts:

```python
from pydantic import BaseModel, Field

class ResearchResult(BaseModel):
    title: str = Field(description="Title of the research")
    summary: str = Field(description="Brief summary")
    key_findings: list[str] = Field(description="List of key findings")
    sources: list[str] = Field(description="List of sources used")

class DraftReport(BaseModel):
    research: ResearchResult
    conclusion: str
```

Create agents with structured output:

```python
from pydantic_ai import Agent

draft_agent = Agent(
    model,
    output_type=DraftReport,  # ← Mandatory!
    instructions="Research the topic...",
)
```

The LLM MUST produce data matching DraftReport. If it doesn't, Pydantic validates, catches the error, and asks the LLM to retry automatically.

## Dependency Injection

Inject dependencies via RunContext:

```python
from dataclasses import dataclass
from pydantic_ai import RunContext

@dataclass
class ResearchDeps:
    topic: str = ""

async def search_web(ctx: RunContext[ResearchDeps], query: str) -> str:
    """Search the web."""
    # ctx.deps.topic is available here
    ...

draft_agent.tool(search_web)
```

## Auto-Retry on Validation Failure

Pydantic AI's key differentiator:

```
LLM output -> Pydantic validates -> ValidationError("must contain keyword") ->
Pydantic AI sends error to LLM -> LLM retries with keyword -> Success
```

No other framework does this automatically. The LLM gets the validation error and fixes itself.

## Known Issues

- **chat_template_kwargs nesting**: Must be nested inside `extra_body` for llama.cpp:
  ```python
  "extra_body": {"chat_template_kwargs": {"enable_thinking": False}}
  ```
- **UsageLimitExceeded**: When validation is impossible, Pydantic AI retries until the limit (default 50 requests).
- **Structured output requires good schemas**: Vague Field descriptions lead to poor LLM output.

## Comparison

| Aspect | LangGraph | Pydantic AI |
|--------|-----------|-------------|
| State management | TypedDict or BaseModel | **output_type (mandatory)** |
| Routing | Conditional edges in graph | Sequential (you code the flow) |
| Validation | Optional (manual) | **Mandatory (auto-retry)** |
| Complexity | High (graph, state, edges) | **Low (Agent + output_type)** |
| Type safety | Runtime | **Compile-time (IDE catches errors)** |

## Requirements

- Python 3.10+
- `pydantic-ai` — Pydantic AI framework
- `openai` — OpenAI-compatible API client (from shared)
- `ddgs` — DuckDuckGo search (from shared)
