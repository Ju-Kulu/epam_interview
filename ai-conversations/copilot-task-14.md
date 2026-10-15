# Task 14 - Improve Markdown-Aware Document Chunking

## Task name and goal

Improve document chunking so that Markdown paragraphs, sections, and sentences are preserved where possible, reducing broken context in RAG retrieval.

## Prompt Summary

Updated `backend/app/ingestion.py` to introduce Markdown-aware chunking helpers:

* `_markdown_block_spans()` identifies paragraph breaks and Markdown block starts.
* `_split_long_span()` splits oversized spans using whitespace boundaries where possible, with character-based fallback.
* `_document_chunk_spans()` prefers sentence boundaries when a Markdown block exceeds the configured chunk size.
* `_pack_chunk_spans()` packs spans into bounded chunks and applies deterministic overlap.
* `chunk_documents()` uses the new helpers while preserving the existing function signature, metadata, and deterministic chunk ID format.

## Tests Added or Updated

Updated `backend/tests/test_ingestion.py` to cover:

* Paragraph-boundary splitting.
* Sentence-boundary splitting.
* Fallback splitting for oversized sentences and long tokens.
* Chunk-size limits.
* Overlap behavior.
* Content preservation and deterministic output.
* Existing document loading, metadata, validation, and empty-document behavior.

## Files Changed

Task 14 implementation:

* `backend/app/ingestion.py`
* `backend/tests/test_ingestion.py`

Other changes present in the supplied working diff:

* `ai-conversations/raw_prompts.md` - Task 14 prompt appended.
* `README.md` - local Ollama setup documentation added.

The README change appears related to local AI provider setup rather than the chunking implementation.

## Tests and result

**Status: Pending verification.**

The supplied diff does not include actual test execution output.

Required commands:

From the repository root:

```powershell
pytest backend/tests/test_ingestion.py -q
pytest backend/tests -q
```

Record the actual results here after execution. Do not mark the task as passing until the commands have completed successfully.

## Important decisions / assumptions

* Existing RAG orchestration and vector-store code were left unchanged.
* Existing ChromaDB records are not automatically replaced by this chunking change.
* Re-indexing must be verified separately to ensure obsolete chunks do not remain in the active collection.
* Review chunk overlap and content-preservation behavior using the actual test results before re-indexing.
pytest backend/tests/test_ingestion.py -q pytest backend/tests -q