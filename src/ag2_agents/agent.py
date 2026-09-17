"""
Agent definitions for AG2 (AutoGen) v1.0+.

AG2 v1.0 is async-first. This package uses its own isolated venv
to avoid dependency conflicts with other frameworks.
"""

import asyncio
import ag2
from ag2.config import OpenAIConfig


# LLM config
LLM_CONFIG = OpenAIConfig(
    model="Qwen3.8-27B-UD-Q3_K_XL.gguf",
    api_key="not-needed",
    base_url="http://localhost:8124/v1",
    temperature=0.7,
    max_tokens=2048,
)


def create_researcher():
    """Create a Researcher agent."""
    return ag2.Agent(
        name="Researcher",
        prompt="You are a helpful assistant. Answer concisely.",
        config=LLM_CONFIG,
    )


def run_single_agent(topic: str) -> str:
    """Run a single agent to research and answer a question.

    Args:
        topic: The research topic.

    Returns:
        The agent's response text.
    """
    print(f"\n{'=' * 60}")
    print(f"AG2 Single Agent: {topic}")
    print(f"{'=' * 60}\n")

    agent = create_researcher()
    response = _run_async(agent, topic)

    print(f"\n{'=' * 60}")
    print("AGENT RESPONSE:")
    print(f"{'=' * 60}")
    print(response)

    return str(response)


def _run_async(agent, topic: str) -> str:
    """Run agent asynchronously and extract response."""
    async def _inner():
        async with agent.run(f"Research and analyze: {topic}") as run_obj:
            reply = await run_obj.result()
            events = await reply.history.get_events()
            for event in events:
                if hasattr(event, 'content') and event.content:
                    return event.content
            return "No response generated."

    # Handle both new and existing event loops
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        return asyncio.run(_inner())
    else:
        return loop.run_until_complete(_inner())
