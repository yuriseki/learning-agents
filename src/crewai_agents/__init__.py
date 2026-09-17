"""
CrewAI — Role-driven multi-agent orchestration.

In CrewAI, agents have distinct personas (role + goal + backstory) and tasks
are assigned to specific agents. The Crew orchestrates execution automatically.

Key concepts:
    - Agent: role + goal + backstory + tools + safety net
    - Task: description + expected_output + agent + context (handoff)
    - Crew: agents + tasks + kickoff() (orchestration)

CRITICAL: Safety net lives on the Agent constructor, NOT the Task.
Always use BOTH max_iter AND max_execution_time with local models.
"""

__all__ = []
