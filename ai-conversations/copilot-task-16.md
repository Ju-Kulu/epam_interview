# Task 16 - Safely remove stale chunks during reindexing

## Task name and goal
Safely remove stale chunks during reindexing while preserving unrelated documents and existing records until embeddings validate and upsert succeeds.

## Prompt summary
Update `VectorStore.index_chunks()` to replace/update incoming chunks and then delete obsolete IDs only for documents represented in that batch. Keep empty input a no-op, preserve provider behavior and collection naming, and test cleanup ordering, failures, idempotency, and unrelated document preservation with fakes.

## Implementation / result
`index_chunks()` now validates all embeddings before collection writes, upserts the incoming records, then fetches existing IDs/metadata separately for each represented document and deletes only IDs missing from that document's incoming set. Empty input returns without collection access. Added fake collection behavior and tests for stale cleanup, updates/new chunks, unrelated documents, embedding and upsert failures, empty input, and repeated indexing.

## Files changed
- `backend/app/vector_store.py` - stale-record cleanup after successful upsert.
- `backend/tests/test_vector_store.py` - fake `get`/`delete` support and focused lifecycle tests.
- `ai-conversations/copilot-task-16.md` - this task record.

## Tests and result

- `python -m pytest backend/tests/test_vector_store.py -q` - **21 passed**.
- `python -m pytest backend/tests -q` - **68 passed, 2 warnings**.

The warnings are existing Starlette/TestClient deprecation warnings. No tests failed or remained unrun.

## Important decisions / assumptions
Cleanup uses Chroma's metadata-filtered `get(where={"document": document}, include=["metadatas"])`, then deletes only returned IDs whose metadata confirms the matching document and which are absent from the incoming IDs. This avoids touching unrelated documents. Embeddings are generated and validated before `upsert`; `get`/`delete` happen only after `upsert` returns successfully. Existing collections are neither cleared nor recreated. Chroma operations are not treated as transactional.

## Corrections / limitations
The current `raw_prompts.md` already contained the complete Task 16 prompt as a user edit before implementation; it was preserved without modification or duplication. The editor reports the existing `openai` and `chromadb` imports unresolved in its selected interpreter, but the tests use injected fakes and passed. No live Chroma service was exercised; if Chroma deletion fails after upsert, the incoming upsert may already be committed, since no transaction guarantee is assumed.
