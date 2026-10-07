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
		"Answer the question using only the supplied knowledge-base context. "
		"Do not invent facts. If the context does not contain enough information, "
		f"respond: {INFORMATION_UNAVAILABLE} "
		"Do not generate, alter, or invent citation metadata.\n\n"
		f"Knowledge-base context:\n{context}\n\n"
		f"Question:\n{question}"
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
