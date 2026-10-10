# Task 15 - Keep Markdown Section Headings with Their Content

## Task name and goal
Keep Markdown section headings with the first content block they introduce whenever that combined group fits within a chunk, while preserving chunk limits, ordering, overlap, and content.

## Prompt summary
Improve Markdown chunking so section headings stay together with their following content, especially short paragraphs, bullet lists, and numbered lists. Preserve the existing chunk-size limit, overlap, content, and deterministic chunk IDs. Add focused tests covering heading grouping and cases where a heading and its content exceed the chunk-size limit. Avoid unrelated changes and preserve existing project behavior.

## Implementation / result
Added a grouping pass that pairs a Markdown heading with the following paragraph, or with a contiguous list, when the combined source span fits in `chunk_size`. The group is packed atomically so it moves to the next chunk rather than leaving its heading behind. If the combined span cannot fit, existing sentence-aware and word-aware fallback splitting still applies.

## Files changed
- `backend/app/ingestion.py`
- `backend/tests/test_ingestion.py`
- `ai-conversations/raw_prompts.md`
- `ai-conversations/copilot-task-15.md`

## Tests and result
From `backend/`:

- `pytest tests/test_ingestion.py -q` - **21 passed**.
- `pytest tests -q` - **63 passed, 2 warnings**.

The warnings are existing Starlette/TestClient deprecations.

## Corrections / limitations
Heading-plus-content grouping is preferred only when the combined group fits within the chunk size; otherwise the existing splitting rules take precedence. A pre-existing `README.md` modification was observed and left untouched.
