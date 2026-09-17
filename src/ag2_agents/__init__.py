"""
AG2 (AutoGen) — Conversational multi-agent with async messaging.

AG2 uses a conversational model where agents are ConversableAgent instances
that exchange messages asynchronously. Unlike CrewAI's task chain or
LangGraph's state graph, AG2 agents communicate via async messaging —
like a group chat where each agent takes turns responding.

Key concepts:
    - ConversableAgent: agents send/receive messages via initiate_chat()
    - is_termination_msg: lambda that checks if conversation should end
    - max_turns: fallback termination (per-agent responses, not total messages)
    - Human-in-the-loop: UserProxyAgent with human_input_mode

Note: Package is `ag2`, import is `autogen`.
"""

__all__ = []
