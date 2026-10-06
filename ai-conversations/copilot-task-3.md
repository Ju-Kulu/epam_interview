# Task 3 - Document Chunking

## Task name / goal
Split loaded knowledge-base documents into deterministic character-based chunks for later embedding and retrieval.

## Prompt / instructions given
**Prompt summary:** Add a `DocumentChunk` dataclass and `chunk_documents(documents, chunk_size=500, overlap=50)`. Preserve source metadata, validate size/overlap, handle blank text sensibly, and cover the behavior with unit tests. Do not implement embeddings or other RAG stages.

## Implementation / result
Added deterministic IDs in `<document>-<index>` form, retained document name/title on each chunk, and used `chunk_size - overlap` as the next slice offset. Empty or whitespace-only text produces no chunks; invalid parameter values raise `ValueError`.

## Files changed
- `backend/app/ingestion.py`
- `backend/tests/test_ingestion.py`

## Tests run and result
`python -m pytest tests -q` from `backend/`: **12 passed**.

## Decisions, assumptions, or corrections
Chunking is character-based as requested. A later formatting-only check found four-space indentation, no trailing whitespace, and final newlines already present, so it required no edits.
