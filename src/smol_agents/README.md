# Smolagents

The agent writes and executes Python code instead of making JSON tool calls. More expressive, more dangerous.

## Quick Start

```bash
# Install shared dependencies
pip install -r ../shared/requirements.txt

# Install Smolagents dependencies
pip install -r requirements.txt

# Run the agent
python3 main.py                    # Default topic
python3 main.py "Python 3.14"     # Custom topic

# Run tests
python3 test.py
```

## The Code-as-Tool Pattern

Instead of JSON tool calls, the agent writes Python code:

```python
# What the agent writes:
results = web_search(query="Python 3.14 release")
# Process results with whitelisted imports
parsed = [r for r in results if "key" in r]
```

The code is executed in a sandboxed `LocalPythonInterpreter` that:
- Only allows whitelisted imports
- Caps total operations (prevents infinite loops)
- Blocks dangerous operations (shell commands, arbitrary module access)

## Configuration

```python
from smolagents import CodeAgent, LiteLLMModel, DuckDuckGoSearchTool

model = LiteLLMModel(
    model_id="openai/Qwen3.6-27B",
    api_base="http://localhost:8124/v1",
    api_key="not-needed",
    custom_llm_provider="openai",
)

agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    additional_authorized_imports=["math", "json", "re"],
    max_steps=10,
)
```

## Sandbox Design

| Aspect | Detail |
|--------|--------|
| Whitelist | `additional_authorized_imports` defines allowed modules |
| Default | `re, itertools, collections, statistics, random, math, queue, stat, time, datetime` |
| Safety cap | `max_steps` limits code execution iterations |
| CVE | smolagents < 1.17.0 has sandbox escape (CVE-2025-5120) |

## Known Issues

- **CVE-2025-5120**: Sandbox escape via crafted code execution. Fixed in v1.17.0.
- **Sandbox is defense-in-depth, NOT a security boundary**. For production, use E2B/Blaxel/Docker.
- **Missing imports cause ImportError**: You must think ahead about needed modules.
- **Code syntax matters**: The agent must write valid Python. Smaller models (<12B) struggle.

## Comparison

| Aspect | From-Scratch | Strands | Smolagents |
|--------|-------------|---------|------------|
| Tool calls | JSON | Framework-managed | **Python code** |
| Sandbox | N/A | N/A | **LocalPythonInterpreter** |
| Error-prone | Low | Low | **Higher** (code syntax matters) |
| Expressiveness | Low | Low | **High** (full Python) |
| Multi-agent | String passing | String passing | String passing |

## Requirements

- Python 3.10+
- `smolagents` — Smolagents framework (>= 1.17.0 for CVE fix)
- `openai` — OpenAI-compatible API client (from shared)
- `ddgs` — DuckDuckGo search (from shared)
