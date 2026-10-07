from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Request payload for the chat endpoint."""

    question: str = Field(..., min_length=1, description="User question to answer from the knowledge base.")

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Question must not be empty.")
        return cleaned


class SourceReference(BaseModel):
    chunk_id: str
    document: str
    title: str | None = None
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
