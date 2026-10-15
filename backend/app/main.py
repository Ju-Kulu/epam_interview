"""FastAPI endpoints for the enterprise knowledge-base assistant."""

from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from app.ingestion import load_documents

from app.indexing import index_knowledge_base
from app.models import ChatRequest, ChatResponse, SourceReference
from app.rag import RAGResponse, answer_question


@asynccontextmanager
async def lifespan(app: FastAPI):
    index_knowledge_base()
    yield


app = FastAPI(title="Enterprise Knowledge Base RAG Chatbot", lifespan=lifespan)


def get_rag_function() -> Callable[[str], RAGResponse]:
    """Provide the RAG function as an overrideable endpoint dependency."""
    return answer_question


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/documents/{document_id}")
def get_document(document_id: str) -> dict[str, str | None]:
    """Return a knowledge-base document by its identifier."""
    documents = load_documents()

    for document in documents:
        if document.name == document_id:
            return {
                "document": document.name,
                "title": document.title,
                "content": document.text,
            }

    raise HTTPException(status_code=404, detail="Document not found.")


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    rag_function: Callable[[str], RAGResponse] = Depends(get_rag_function),
) -> ChatResponse:
    result = rag_function(request.question)
    return ChatResponse(
        answer=result.answer,
        sources=[
            SourceReference(
                chunk_id=source.chunk_id,
                document=source.document,
                title=source.title,
                distance=source.distance,
            )
            for source in result.sources
        ],
    )
