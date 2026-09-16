# From-Scratch ReAct Agent

A minimal agent built without any framework. Implements the core patterns that every agent framework abstracts: ReAct loops, tool calling, message management, and termination conditions.

## Quick Start

```bash
# Install shared dependencies
pip install -r ../shared/requirements.txt

# Run the agent
python3 main.py                    # Default topic
python3 main.py "Python 3.14"     # Custom topic

# Run tests
python3 test.py
```

## How It Works

### The ReAct Loop

```
1. Send conversation + tool schemas → LLM
2. LLM responds with tool calls OR final answer
3. If tool calls: execute → feed results back → repeat from step 1
4. If final answer: return it and stop
```

### Message Management

The agent's memory is a list of messages:
- `system` — role instructions + tool awareness
- `user` — the task or question
- `assistant` — LLM responses (with or without tool calls)
- `tool` — results from executed tools

### Termination

The agent stops when:
- LLM responds WITHOUT tool calls (final answer)
- Max iterations reached (safety net)
- LLM endpoint error (graceful degradation)

## Architecture

```
SimpleAgent
├── __init__()          — Set up LLM client, system message
├── _init_system_message() — Add role instructions
├── run()               — ReAct loop: thought → action → observation
└── _parse_arguments()  — Parse JSON from LLM tool calls
```

## Multi-Agent Pipeline

```
ResearcherAgent (uses search tool)
    ↓ string output
WriterAgent (formats into report)
```

No shared state, no message queue, no framework — just Python string passing.

## Usage Example

```python
from from_scratch.agent import SimpleAgent

agent = SimpleAgent(
    name="Researcher",
    instructions="Search the web and summarize findings.",
    max_iterations=10,
)

result = agent.run("Search for Python 3.14 release notes.")
print(result)
```

## Configuration

Set environment variables (see `../shared/README.md`):

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BASE_URL` | `http://localhost:8123/v1` | LLM endpoint |
| `LLM_MODEL` | `Qwen3.6-27B` | Model name |
| `LLM_API_KEY` | `not-needed` | API key |
| `LLM_MAX_TOKENS` | `4096` | Max output tokens |
| `LLM_DISABLE_THINKING` | `true` | Disable reasoning mode |

## Known Issues

- **Search rate limits**: DuckDuckGo may rate-limit from Docker sandboxes
- **Model size matters**: Smaller models (<12B) struggle with tool calling
- **No built-in memory**: Conversation history grows without bound
- **No error recovery**: Tool failures are reported but not retried

## Requirements

- Python 3.10+
- `openai` — OpenAI-compatible API client (from shared)
- `ddgs` — DuckDuckGo search (from shared)
