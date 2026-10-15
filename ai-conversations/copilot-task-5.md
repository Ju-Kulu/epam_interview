# Task 5 - Retrieval/Search

## Task name / goal
Retrieve the most relevant indexed document chunks for a user's question.

## Prompt / instructions given
**Prompt summary:** Add only a retrieval method to the existing `VectorStore`. Validate the query and `top_k`, embed the query with the configured OpenAI embedding model, query the existing ChromaDB collection, and return typed results preserving source metadata and distance. Add unit tests with fake clients; do not implement LLM calls or later RAG stages.

## Implementation summary
- Added the `RetrievedChunk` dataclass.
- Added `VectorStore.search()` with query and `top_k` validation (`top_k` defaults to 3).
- Embeds the query using the same configured model as indexing and queries ChromaDB for nearest chunks.
- Converts ChromaDB results to typed `RetrievedChunk` objects, preserving metadata and distance.
- Keeps ChromaDB response parsing inside `vector_store.py`.

## Files changed
- `backend/app/vector_store.py`
- `backend/tests/test_vector_store.py`

## Tests
The backend test suite passed: **20 tests passed**. Tests used fake clients; no real API calls were made.

## Important decisions / assumptions
Retrieval reuses the configured embedding model from indexing. ChromaDB remains an implementation detail of `VectorStore`, and fake clients exercise the retrieval flow without external services.
