# CrewAI

Role-driven multi-agent orchestration. Agents have distinct personas, tasks have handoff, Crew orchestrates automatically.

## Quick Start

```bash
# Install shared dependencies
pip install -r ../shared/requirements.txt

# Install CrewAI dependencies
pip install -r requirements.txt

# Run the crew
python3 main.py                    # Default topic
python3 main.py "Python 3.14"     # Custom topic

# Run tests
python3 test.py
```

## The Role-Driven Design

Each agent has a distinct persona:

```python
from crewai import Agent, LLM

agent = Agent(
    role="Senior Research Analyst",
    goal="Find accurate, up-to-date information...",
    backstory="You are a meticulous researcher with 15 years...",
    tools=[WebsiteSearchTool()],
    llm=LLM(model="Qwen3.6-27B", base_url="http://localhost:8124/v1"),
    max_iter=10,
    max_execution_time=120,
)
```

## Task Handoff

Tasks flow data between agents via `context`:

```python
from crewai import Task

# First task: no context
research = Task(
    description="Research the topic...",
    agent=researcher,
)

# Second task: sees Researcher's output
writing = Task(
    description="Write a report based on findings...",
    agent=writer,
    context=[research],  # Handoff!
)

# Third task: sees Writer's output
review = Task(
    description="Review the report...",
    agent=reviewer,
    context=[writing],  # Handoff!
)
```

## Crew Orchestration

The Crew runs everything automatically:

```python
from crewai import Crew

crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research, writing, review],
    verbose=True,
)

result = crew.kickoff()  # Runs sequentially: Research -> Write -> Review
```

## Dual Safety Net

CRITICAL: Always use BOTH parameters on the Agent constructor:

```python
agent = Agent(
    role="Researcher",
    max_iter=10,              # Max iterations (UNRELIABLE with local models)
    max_execution_time=120,   # Hard timeout in seconds (RELIABLE)
)
```

`max_iter` alone may not stop the agent with local models. `max_execution_time` is your backup.

## Known Issues

- **Python < 3.14 required**: CrewAI doesn't support Python 3.14+. Use Python 3.12.
- **max_iter unreliability**: Local models may ignore max_iter. Always add max_execution_time.
- **Safety net on Agent, NOT Task**: A common mistake is putting safety params on Task.
- **Persona design matters**: Without distinct personas, all agents behave the same.

## Comparison

| Aspect | From-Scratch | Strands | Smolagents | CrewAI |
|--------|-------------|---------|------------|--------|
| Tool calls | JSON | Framework | Python code | JSON |
| Orchestration | Manual | Manual | Manual | **Automatic** |
| Multi-agent | String passing | String passing | String passing | **Task context** |
| Safety net | max_iterations | N/A | max_steps | **max_iter + timeout** |
| Feedback loop | No | No | No | No |

## Requirements

- Python 3.10-3.13 (NOT 3.14+)
- `crewai` — CrewAI framework
- `crewai-tools` — Built-in tools (web search, etc.)
- `openai` — OpenAI-compatible API client (from shared)
- `ddgs` — DuckDuckGo search (from shared)
