"""
Pydantic AI — Type-safe structured agents with validation-first design.

Pydantic AI uses Pydantic models to define output contracts. The LLM MUST
produce data matching the schema. If it doesn't, Pydantic validates, catches
the error, and asks the LLM to retry automatically.

Key concepts:
    - output_type: Pydantic model defining the output contract (MANDATORY)
    - deps_type: Dependency injection via RunContext
    - model_settings: Shared config (temperature, max_tokens, etc.)
    - Auto-retry: Validation failure -> error sent to LLM -> LLM retries

Compare to from-scratch:
    - From-scratch: raw string output, manual parsing
    - Pydantic AI: structured output, automatic validation + retry
"""

__all__ = []
