# Task 2 - Knowledge-Base Document Loader

## Task name / goal
Load the existing Markdown knowledge-base documents into a simple internal representation.

## Prompt / instructions given
**Prompt summary:** Implement only synchronous Markdown loading in `backend/app/ingestion.py`; return document name, optional title, and full text; validate missing/empty data directories; add focused unit tests using temporary directories. Do not implement chunking or later RAG components.

## Implementation / result
Added an immutable `LoadedDocument` dataclass and `load_documents()`. It reads sorted top-level Markdown files from the default repository `data/` directory (or a supplied path), extracts the first H1 title, and raises clear errors for a missing directory or no supported documents.

## Files changed
- `backend/app/ingestion.py`
- `backend/tests/test_ingestion.py`

## Tests run and result
`python -m pytest tests -q` from `backend/`: **3 passed**.

## Decisions, assumptions, or corrections
The `data/README.md` is folder documentation, not a knowledge-base article, so the loader excludes it. Tests create their own temporary Markdown files and do not depend on repository data.
