"""
Pydantic models for structured output.

These models define the OUTPUT CONTRACT. The LLM MUST produce data
matching this exact structure. If it doesn't, Pydantic validates,
catches the error, and asks the LLM to retry.
"""

from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    """Research findings on a topic."""
    title: str = Field(description="Title of the research")
    summary: str = Field(description="Brief summary of the research")
    key_findings: list[str] = Field(description="List of key findings (bullet points)")
    sources: list[str] = Field(description="List of sources used")


class DraftReport(BaseModel):
    """Draft report from the research agent."""
    research: ResearchResult = Field(description="Research findings")
    conclusion: str = Field(description="Brief conclusion")


class ReviewResult(BaseModel):
    """Review result from the review agent."""
    approved: bool = Field(description="Whether the draft is approved for finalization")
    quality_score: int = Field(ge=1, le=5, description="Quality score 1-5")
    feedback: str = Field(description="Specific feedback for improvement")


class FinalReport(BaseModel):
    """Final research report after review and revision."""
    research: ResearchResult = Field(description="Research findings")
    conclusion: str = Field(description="Final polished conclusion")
    revisions_made: str = Field(description="What was improved based on review feedback")
