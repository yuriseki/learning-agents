# AG2 (AutoGen)

Conversational multi-agent with async messaging. Agents exchange messages like a group chat.

## Quick Start

```bash
# Install shared dependencies
pip install -r ../shared/requirements.txt

# Install AG2 dependencies
pip install -r requirements.txt

# Run the debate
python3 main.py                    # Default problem
python3 main.py "Your problem"     # Custom problem

# Run tests
python3 test.py
```

## The Conversational Model

Agents exchange messages asynchronously:

```python
from autogen import ConversableAgent, LLMConfig

# Proposer: suggests solutions, revises based on feedback
proposer = ConversableAgent(
    name="Proposer",
    system_message="You suggest solutions...",
    llm_config=LLMConfig({"api_type": "openai", "model": "Qwen3.6-27B", ...}),
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "AGREED" in msg.get("content", ""),
)

# Critic: reviews proposals, provides feedback
critic = ConversableAgent(
    name="Critic",
    system_message="You review proposals...",
    llm_config=LLMConfig({...}),
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "APPROVED" in msg.get("content", ""),
)

# Start the conversation
result = proposer.initiate_chat(
    recipient=critic,
    message="Here's a problem to solve...",
    max_turns=6,  # Per-agent responses (not total messages)
)
```

## Termination Conditions

Two ways to stop the conversation:

1. **Keyword detection**: `is_termination_msg` lambda checks each message
2. **Max turns fallback**: `max_turns` limits per-agent responses

```python
# Stops when EITHER agent says the keyword
is_termination_msg=lambda msg: "AGREED" in msg.get("content", "") or "APPROVED" in msg.get("content", "")

# Fallback: max 6 responses per agent (12 total messages)
max_turns=6
```

## Known Issues

- **Import is `autogen`, not `ag2`**: Package is `ag2`, import is `autogen`. This is confusing.
- **Token-heavy**: Every turn includes full conversation history. A 6-round debate = ~12K tokens.
- **max_turns = per-agent**: `max_turns=3` = 3 Proposer + 3 Critic = 6 total messages.
- **Python-only**: AG2 has no TypeScript support.
- **Direction matters**: The agent calling `initiate_chat()` sends the FIRST message.

## Comparison

| Aspect | CrewAI | AG2 | LangGraph |
|--------|--------|-----|-----------|
| Orchestration | Sequential tasks | **Conversation loop** | State graph |
| Feedback loop | No | **Yes** (Critic <-> Proposer) | Yes (revision) |
| Termination | max_iter + timeout | **Keyword + max_turns** | Conditional edges |
| Human-in-loop | Not built-in | **UserProxyAgent** | Manual |
| Multi-agent | Task context | **Async messaging** | State graph |

## Requirements

- Python 3.8+
- `ag2` — AG2 (AutoGen) framework
- `openai` — OpenAI-compatible API client (from shared)
- `ddgs` — DuckDuckGo search (from shared)
