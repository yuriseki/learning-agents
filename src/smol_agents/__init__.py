"""
Smolagents — Code-as-tool agent with sandboxed execution.

The key difference from all other frameworks: the agent WRITES PYTHON CODE
that calls tools, not JSON tool calls. The code is executed in a sandboxed
LocalPythonInterpreter that:
- Only allows whitelisted imports
- Caps total operations (prevents infinite loops)
- Blocks dangerous operations (shell commands, arbitrary module access)

Flow: Agent writes code -> Interpreter executes -> Output returned -> Agent writes more code.

Compare to from-scratch:
    - From-scratch: LLM outputs JSON {"name": "search", "args": {...}}
    - Smolagents: LLM outputs Python code: results = web_search("query")

Compare to Strands:
    - Strands: @tool decorator + framework dispatch
    - Smolagents: Python code execution + sandbox boundary
"""

__all__ = []
