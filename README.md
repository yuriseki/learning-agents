# Learning Agents

Multi-agent AI framework experiments using local LLMs. Built for learning, not production.

## Overview

Hands-on experiments with 7 major agentic frameworks, each implementing the same research pipeline: **search the web → analyze → produce a report**. Compare architectures, trade-offs, and failure modes side by side.

## Frameworks

| # | Package | Framework | Pattern | Complexity |
|---|---------|-----------|---------|------------|
| 0 | [`from_scratch`](src/from_scratch/) | Manual ReAct + message passing | Hand-written loop | Low |
| 1 | [`strands_agents`](src/strands_agents/) | Strands Agents (AWS) | 3 primitives | Low |
| 2 | [`smol_agents`](src/smol_agents/) | Smolagents (Hugging Face) | Code-as-tool | Medium |
| 3 | [`crewai_agents`](src/crewai_agents/) | CrewAI | Role-driven orchestration | Medium |
| 4 | [`ag2_agents`](src/ag2_agents/) | AG2 (AutoGen) v1.0 | Conversational async | Medium |
| 5 | [`langgraph_agents`](src/langgraph_agents/) | LangGraph | Stateful directed graphs | High |
| 6 | [`pydantic_agents`](src/pydantic_agents/) | Pydantic AI | Type-safe structured output | Low |

## Quick Start

### Prerequisites

- **Python 3.12** (via `uv` or `pyenv`)
- **llama.cpp server** running on `localhost:8124`
- **Model**: Qwen3.8-27B (or any OpenAI-compatible endpoint)

### Setup

```bash
# Create virtual environment
uv venv .venv --python 3.12
source .venv/bin/activate

# Install all framework dependencies (single file)
pip install -r requirements.txt

# AG2 needs its own venv (dependency conflicts)
cd src/ag2_agents
uv venv .venv --python 3.12
.venv/bin/pip install "ag2[openai]" openai ddgs
cd ../..
```

> **Note**: `requirements.txt` installs all 6 frameworks into a single venv. AG2 is excluded because it requires `openai>=3.0`, while other frameworks need `openai<3.0`.

### Run

```bash
cd /path/to/learning-agents

# Most frameworks (shared venv)
PYTHONPATH=src/ .venv/bin/python src/strands_agents/main.py "Your topic"
PYTHONPATH=src/ .venv/bin/python src/smol_agents/main.py "Your topic"
PYTHONPATH=src/ .venv/bin/python src/crewai_agents/main.py "Your topic"
PYTHONPATH=src/ .venv/bin/python src/langgraph_agents/main.py "Your topic"
PYTHONPATH=src/ .venv/bin/python src/pydantic_agents/main.py "Your topic"

# AG2 (isolated venv)
cd src/ag2_agents && .venv/bin/python main.py "Your topic"
```

### Test

```bash
cd /path/to/learning-agents

# Most frameworks
PYTHONPATH=src/ .venv/bin/python src/smol_agents/test.py
PYTHONPATH=src/ .venv/bin/python src/crewai_agents/test.py
# ... etc

# AG2
cd src/ag2_agents && .venv/bin/python test.py
```

### DDEV

Alternatively, run everything inside a [DDEV](https://ddev.com) container. No local Python or `uv` needed: the container provisions Python 3.12 and both venvs on first start.

```bash
ddev start                        # build image, create venvs, install all deps (idempotent)
ddev agent strands "Your topic"   # run a framework; short or full package name
ddev agent ag2 "Your problem"
ddev test all                     # or a single one: ddev test smol
ddev ssh                          # shell with the shared venv already activated
ddev setup --force                # rebuild the venvs from scratch
```

`localhost:8124` inside the container is forwarded to the host, so a local llama.cpp server works unchanged as long as it listens on all interfaces (`llama-server --host 0.0.0.0 ...`). `.env` is picked up as usual. Container venvs live in `.ddev/.venv` and `.ddev/.venv-ag2`, separate from the host venvs.

## Architecture

Each package follows the same structure:

```
src/<framework>/
├── __init__.py      # Package exports
├── agent.py         # Agent definitions + pipeline
├── main.py          # Entry point
├── test.py          # Verification script
├── requirements.txt # Dependencies
└── README.md        # Framework-specific notes
```

### Shared Module

[`src/shared/`](src/shared/) provides common utilities:

| Module | Purpose |
|--------|---------|
| `config.py` | LLM endpoint configuration (env vars + defaults) |
| `tools.py` | DuckDuckGo search tool |
| `test.py` | Shared test utilities |

### Configuration

Set via environment variables (defaults shown):

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BASE_URL` | `http://localhost:8124/v1` | LLM endpoint |
| `LLM_MODEL` | `Qwen3.6-27B` | Model name |
| `LLM_API_KEY` | `not-needed` | API key |
| `LLM_TEMPERATURE` | `0.7` | Sampling temperature |

#### Using OpenAI API

To use OpenAI's cloud API instead of a local model:

```bash
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4o"
export LLM_API_KEY="sk-proj-your-key-here"
```

Or add to a `.env` file:

```bash
cat > .env << 'EOF'
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
LLM_API_KEY=sk-proj-your-key-here
LLM_TEMPERATURE=0.7
EOF

# Load it
set -a && source .env && set +a
```

Works with any OpenAI-compatible provider (Azure, Together, Perplexity, etc.) by changing `LLM_BASE_URL` and `LLM_MODEL`.

#### Using Local llama.cpp (default)

```bash
export LLM_BASE_URL="http://localhost:8124/v1"
export LLM_MODEL="Qwen3.8-27B-UD-Q3_K_XL.gguf"
export LLM_API_KEY="not-needed"
```

## Key Findings

### What Each Framework Teaches

| Framework | Key Lesson |
|-----------|------------|
| From-scratch | Every framework abstracts: ReAct loop, tool dispatch, JSON schemas |
| Strands | 3 primitives (Model, Tools, Agent) reduce ~200 lines to ~80 |
| Smolagents | Code-as-tool: agent writes Python, not JSON. More expressive, more dangerous |
| CrewAI | Role-driven design: persona matters. `context=[task]` handoff is unreliable with local models |
| AG2 | Conversational async: first real feedback loop. `is_termination_msg` + `max_turns` |
| LangGraph | Stateful graphs: conditional routing, feedback loops, checkpointing |
| Pydantic AI | Validation-first: schema mismatch → auto-retry. No other framework does this |

### Local Model Gotchas

- **CrewAI**: `max_iter` alone is unreliable. Always add `max_execution_time`
- **Strands**: No `max_iterations` exposed. Model decides when to stop
- **Smolagents**: `additional_authorized_imports` is the security boundary
- **AG2**: Token-heavy (full conversation history each turn). ~12K tokens for 6-round debate
- **LangGraph**: Use `langchain-openai`, NOT `langchain-ollama`
- **Pydantic AI**: `chat_template_kwargs` must be nested inside `extra_body`

## My Hardware

| Component | Detail |
|-----------|--------|
| GPU | R9700 32GB (ROCm) + RX 7900 XT 20GB (Vulkan) |
| Backend | Vulkan (both GPUs) |
| Primary Model | Qwen3.8-27B (Q3_K_XL) |
| Inference | llama.cpp server on `localhost:8124` |

## License

Experimental/educational. Not for production use.
