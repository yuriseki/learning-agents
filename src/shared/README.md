# Shared Module

Common LLM configuration and reusable tools for the Learning AI Agents blog series.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test the module
python3 test.py
```

## Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BASE_URL` | `http://localhost:8123/v1` | OpenAI-compatible API endpoint |
| `LLM_MODEL` | `Qwen3.6-27B` | Model name/ID |
| `LLM_API_KEY` | `not-needed` | API key (for local models) |
| `LLM_MAX_TOKENS` | `4096` | Max output tokens |
| `LLM_TEMPERATURE` | `0.7` | Sampling temperature |
| `LLM_DISABLE_THINKING` | `true` | Disable reasoning/thinking mode |

### Docker Sandbox

When running inside a Docker sandbox, set:

```bash
export LLM_BASE_URL=http://172.17.0.1:8123/v1
```

## Usage

```python
from shared.config import LLM_BASE_URL, LLM_MODEL, LLM_API_KEY, LLM_EXTRA_BODY
from shared.tools import search_web, TOOLS

# Config
print(f"Endpoint: {LLM_BASE_URL}")
print(f"Model: {LLM_MODEL}")

# Tools
results = search_web("Python 3.14", max_results=3)
print(results)
```

## Framework Adaptation

Each framework package adapts the shared config to its own API:

| Framework | Adaptation |
|-----------|------------|
| From-scratch | `OpenAI(base_url=LLM_BASE_URL, ...)` |
| Strands | `OpenAIModel(client_args={...}, ...)` |
| Smolagents | `LiteLLMModel(model_id=..., api_base=LLM_BASE_URL, ...)` |
| CrewAI | `LiteLLM(model=..., api_base=LLM_BASE_URL, ...)` |
| AG2 | `config_list=[{"model": ..., "base_url": ...}]` |
| LangGraph | `ChatOpenAI(model=..., base_url=LLM_BASE_URL, ...)` |
| Pydantic AI | `OpenAIChatModel(model=..., base_url=LLM_BASE_URL, ...)` |

## Requirements

- Python 3.10+
- `openai` — OpenAI-compatible API client
- `ddgs` — DuckDuckGo search (replaces deprecated `duckduckgo-search`)
