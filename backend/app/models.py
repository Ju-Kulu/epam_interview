from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Request payload for the chat endpoint.

    Validation rules will be completed when the API is implemented.
    """

    question: str = Field(..., min_length=1, description="User question to answer from the knowledge base.")

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Question must not be empty.")
        return cleaned


class SourceReference(BaseModel):
    document: str
    section: str
    chunk_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = []
