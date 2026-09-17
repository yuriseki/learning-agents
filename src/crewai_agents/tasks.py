"""
Task definitions with clear handoff between agents.

In CrewAI, Tasks define WHAT work needs to be done. Each task:
    - agent: Which agent does this task
    - expected_output: What the output should look like
    - context: Previous tasks whose outputs feed into this task (handoff!)

NOTE: Context handoff can be unreliable with local models. The Writer
may not receive the Researcher's output via context. As a workaround,
we use a single Research+Write agent for reliable results.
"""

import crewai as _crewai
Task = _crewai.Task
from crewai_agents.agent import create_researcher, create_writer, create_reviewer


def create_tasks(topic: str) -> list:
    """Create the task chain: Research+Write -> Review.

    Uses a single agent for Research+Write to avoid context handoff issues
    with local models. The Researcher has write_file tool to save results.

    Args:
        topic: The research topic.

    Returns:
        List of Task instances in execution order.
    """
    # Task 1: Research AND Write (combined to avoid context handoff issues)
    research_write_task = Task(
        description=(
            f"Research the topic: '{topic}'.\n\n"
            f"Step 1: Use web search to find current, accurate information.\n"
            f"Search multiple times if needed for comprehensive coverage.\n\n"
            f"Step 2: Based on your research, write a complete, well-structured report.\n"
            f"Include: Title, Executive Summary, Key Findings (bullet points),\n"
            f"Detailed Analysis, Conclusion.\n"
            f"Use professional tone and clear formatting.\n\n"
            f"Return the COMPLETE report as your final answer."
        ),
        expected_output=(
            "A complete, professionally formatted report with: "
            "Title, Executive Summary, Key Findings, Detailed Analysis, and Conclusion."
        ),
        agent=create_researcher(),
    )

    # Task 2: Review (context = research+write output)
    review_task = Task(
        description=(
            "Review the report for:\n"
            "- Accuracy: Are facts correct and properly sourced?\n"
            "- Clarity: Is the writing clear and well-organized?\n"
            "- Completeness: Are all important aspects covered?\n"
            "- Formatting: Does it follow professional standards?\n\n"
            "If issues are found, suggest specific improvements.\n"
            "If the report is good, approve it with a brief summary."
        ),
        expected_output="A review with specific feedback, improvement suggestions, or approval.",
        agent=create_reviewer(),
        context=[research_write_task],
    )

    return [research_write_task, review_task]
