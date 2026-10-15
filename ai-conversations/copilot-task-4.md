# Task 4 - Embeddings and Vector Store

## Task name / goal
Embed document chunks with OpenAI and store them in a local persistent ChromaDB collection for later retrieval.

## Prompt / instructions given
**Prompt summary:** Add a small vector-store API that embeds chunks, stores IDs and citation metadata, and avoids duplicate records on repeated indexing. Use the configured embedding model and existing API-key setting. Add mocked unit tests; do not implement search, RAG orchestration, endpoints, frontend, or Docker changes.

## Implementation / result
Added `VectorStore.index_chunks()`, which batches chunk text through the configured OpenAI embedding model and upserts embeddings, text, and document/title/chunk ID metadata into a persistent ChromaDB collection. Chunk IDs are used as Chroma record IDs. Added settings for the embedding model and persistence directory.

## Files changed
- `backend/app/config.py`
- `backend/app/vector_store.py`
- `backend/tests/test_vector_store.py`

`backend/requirements.txt` was not changed: it already declared pinned ChromaDB and OpenAI SDK dependencies.

## Tests run and result
`python -m pytest tests -q` from `backend/`: **15 passed**. Tests use fake ChromaDB and OpenAI clients; no live API calls were made.

## Decisions, assumptions, or corrections
ChromaDB `upsert` makes repeated indexing with stable chunk IDs replace existing records. No credentials were added. The active Python environment lacked the declared ChromaDB/OpenAI packages, so real client construction was not exercised; editor diagnostics reported those imports unresolved.
