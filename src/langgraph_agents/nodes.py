"""
Node functions for the LangGraph pipeline.

Each node:
1. Takes PipelineState (reads whatever it needs)
2. Calls the LLM
3. Returns a partial update (dict with ONLY what changed)
"""

import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

# Add src/ to path for shared module import
_SRC_ROOT = Path(__file__).resolve().parent.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from shared.config import (
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_API_KEY,
    LLM_TEMPERATURE,
    LLM_EXTRA_BODY,
)
from langgraph_agents.state import PipelineState


# Shared model instance — connects to llama.cpp via OpenAI-compatible endpoint
llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
    temperature=LLM_TEMPERATURE,
    max_tokens=4096,
    extra_body=LLM_EXTRA_BODY,
)


@tool
def search_web(query: str) -> str:
    """Search the web using DuckDuckGo. Takes a search query and returns results."""
    print(f"\n  [TOOL] Searching web for: {query}")
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=5)
        formatted = "\n\n".join(
            f"[{i+1}] {r['title']}: {r['body']}" for i, r in enumerate(results)
        )
        return formatted if formatted else "No results found."
    except Exception as e:
        return f"Search error: {e}"


# LLM with tools bound — the model can now request tool calls
llm_with_tools = llm.bind_tools([search_web])


def research_node(state: PipelineState) -> dict:
    """Research node: gather information about the topic using web search.

    Reads: state['topic']
    Writes: research_results

    Uses tool calling: the LLM can request web searches via search_web tool.
    """
    print("\n[RESEARCH] Gathering information...")

    messages = [
        HumanMessage(content=(
            f"Research the topic: '{state['topic']}'.\n\n"
            f"Use the search_web tool to find current information. "
            f"Search multiple times if needed for comprehensive coverage.\n"
            f"Return a comprehensive research summary (2-3 paragraphs) "
            f"based on the search results."
        ))
    ]

    # Run the tool-calling loop (max 3 tool calls to prevent infinite loops)
    max_tool_calls = 3
    for attempt in range(max_tool_calls):
        response = llm_with_tools.invoke(messages)

        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"  [RESEARCH] LLM requested tool call: {response.tool_calls[0]['name']}")

            tool_call = response.tool_calls[0]
            if tool_call["name"] == "search_web":
                tool_result = search_web.invoke(tool_call["args"])
                print(f"  [RESEARCH] Got {len(tool_result)} chars from search")

            messages.append(response)
            messages.append(ToolMessage(
                content=tool_result,
                tool_call_id=tool_call["id"]
            ))
        else:
            return {"research_results": response.content}

    print(f"  [RESEARCH] Max tool calls reached ({max_tool_calls})")
    return {"research_results": response.content}


def draft_node(state: PipelineState) -> dict:
    """Draft node: write initial content from research.

    Reads: state['topic'], state['research_results']
    Writes: draft
    """
    print("\n[DRAFT] Writing initial draft...")

    response = llm.invoke([
        HumanMessage(content=(
            f"Based on this research, write a report on: {state['topic']}\n\n"
            f"RESEARCH:\n{state['research_results']}\n\n"
            f"Format: Title, Introduction, Key Findings, Conclusion.\n"
            f"Keep it concise but informative."
        ))
    ])

    return {"draft": response.content}


def review_node(state: PipelineState) -> dict:
    """Review node: evaluate draft quality and produce feedback.

    Reads: state['draft']
    Writes: review_feedback

    IMPORTANT: The feedback MUST start with either:
    - "APPROVED: [note]" — quality is good, move to finalize
    - "REVISE: [feedback]" — quality needs work, go back to draft
    This enables conditional routing in the graph.
    """
    print("\n[REVIEW] Evaluating draft quality...")

    response = llm.invoke([
        HumanMessage(content=(
            f"Review this draft for quality:\n\n"
            f"--- DRAFT START ---\n{state['draft']}\n--- DRAFT END ---\n\n"
            f"Evaluate:\n"
            f"1. Accuracy: Are facts clear and consistent?\n"
            f"2. Structure: Is it well-organized with clear sections?\n"
            f"3. Completeness: Does it cover the key points?\n\n"
            f"CRITICAL: Start your response with exactly one of:\n"
            f"- 'APPROVED: [brief note]' if quality is acceptable\n"
            f"- 'REVISE: [specific feedback]' if quality needs improvement\n"
        ))
    ])

    return {"review_feedback": response.content}


def revise_node(state: PipelineState) -> dict:
    """Revise node: improve draft based on review feedback.

    Reads: state['draft'], state['review_feedback']
    Writes: draft (overwrites with improved version), revision_count (+1)
    """
    current_count = state.get("revision_count", 0)
    print(f"\n[REVISE] Improving draft (revision #{current_count + 1})...")

    response = llm.invoke([
        HumanMessage(content=(
            f"Improve this draft based on the review feedback.\n\n"
            f"IMPORTANT: Use ONLY the research below for facts.\n\n"
            f"--- RESEARCH ---\n{state['research_results']}\n"
            f"--- DRAFT ---\n{state['draft']}\n"
            f"--- FEEDBACK ---\n{state['review_feedback']}\n"
            f"--- END ---\n\n"
            f"Produce an improved version that addresses the feedback."
        ))
    ])

    return {
        "draft": response.content,
        "revision_count": current_count + 1,
    }


def finalize_node(state: PipelineState) -> dict:
    """Finalize node: produce the final polished output.

    Reads: state['draft']
    Writes: final_output
    """
    print("\n[FINALIZE] Producing final output...")

    response = llm.invoke([
        HumanMessage(content=(
            f"Produce the final polished version of this report.\n\n"
            f"IMPORTANT: Use ONLY the research below for facts.\n\n"
            f"--- RESEARCH ---\n{state['research_results']}\n"
            f"--- DRAFT ---\n{state['draft']}\n"
            f"--- END ---\n\n"
            f"Ensure it is professionally formatted and ready for publication."
        ))
    ])

    return {"final_output": response.content}
