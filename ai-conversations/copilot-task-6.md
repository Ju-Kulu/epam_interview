# Task 6 - RAG Orchestration

## Task name / goal
Connect vector-store retrieval to an LLM and return a grounded answer with its retrieved sources.

## Prompt / instructions given
**Prompt summary:** Implement only the RAG orchestration: search for relevant chunks, build a prompt constrained to retrieved context, call the LLM abstraction, and return the answer with original source metadata. Cover no-results behavior and keep API/frontend/infrastructure work out of scope.

## Implementation summary
- Added `RAGResponse` and `answer_question()` in `backend/app/rag.py`.
- The orchestration passes the question to `VectorStore.search()`, formats only retrieved chunk text as knowledge-base context, and asks the model not to invent facts or citation metadata.
- Returned sources are the original `RetrievedChunk` objects, including chunk ID, document, title, and distance.
- Empty retrieval returns a fixed knowledge-base-unavailable answer without calling the LLM.
- Added a thin configured OpenAI chat-completion wrapper in `backend/app/llm.py` because that module was still a placeholder.

## Files changed
- `backend/app/rag.py`
- `backend/app/llm.py`
- `backend/tests/test_rag.py`
- `ai-conversations/copilot-task-6.md`

## Tests run and actual result
`python -m pytest tests -q` from `backend/`: **24 passed**. RAG tests inject fake dependencies; no real API calls were made.

## Important decisions / assumptions
Prompt construction stays in `rag.py`; OpenAI communication stays in `llm.py`; retrieval/source objects stay with `VectorStore`. The LLM wrapper uses the existing `openai_model` and API-key settings. The LLM integration itself is mocked in tests, so provider behavior was not exercised.
