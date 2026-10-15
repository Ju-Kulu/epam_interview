"""RAG orchestration for grounded knowledge-base answers."""

from dataclasses import dataclass
from typing import Callable

from app.llm import generate_answer
from app.vector_store import RetrievedChunk, VectorStore


INFORMATION_UNAVAILABLE = "The information is not available in the knowledge base."


@dataclass(frozen=True)
class RAGResponse:
    answer: str
    sources: list[RetrievedChunk]


def _build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n".join(chunk.text for chunk in chunks)
    return (
        "You are an enterprise knowledge-base assistant helping customer support teams.\n"
        "Answer the user's question using only facts explicitly supported by the "
        "knowledge-base context below.\n\n"
        "Rules:\n"
        "1. Treat the knowledge-base context as the only source of factual information. Do not invent facts.\n"
        "2. Give relevant troubleshooting steps that are explicitly stated in the context.\n"
        "3. Do not invent causes, procedures, commands, recommendations, or explanations.\n"
        "4. Do not assume that a related symptom proves a specific cause.\n"
        "5. If the context supports a partial answer, provide that answer and clearly "
        "state what specific information is missing.\n"
        f"6. If the context provides no useful answer, respond exactly: "
        f"{INFORMATION_UNAVAILABLE}\n"
        "7. Do not generate or modify source names, document identifiers, or citation metadata.\n\n"
        f"Knowledge-base context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )


def answer_question(
    question: str,
    vector_store: VectorStore | None = None,
    *,
    top_k: int = 3,
    answer_generator: Callable[[str], str] | None = None,
) -> RAGResponse:
    """Retrieve relevant context and generate an answer grounded in it."""
    if not question.strip():
        raise ValueError("question must not be empty or whitespace-only.")

    store = vector_store if vector_store is not None else VectorStore()
    chunks = store.search(question, top_k=top_k)
    if not chunks:
        return RAGResponse(answer=INFORMATION_UNAVAILABLE, sources=[])

    prompt = _build_prompt(question, chunks)
    generate = answer_generator if answer_generator is not None else generate_answer
    answer = generate(prompt)
    return RAGResponse(answer=answer, sources=chunks)
