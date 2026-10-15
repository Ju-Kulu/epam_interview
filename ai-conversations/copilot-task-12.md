# Task 12 - Configurable AI Provider Settings

## Task name and goal

Prepare the application configuration for switching between local Ollama and remote OpenAI providers through environment variables, without changing the existing RAG behavior or implementing provider clients.

The task also includes correcting the conversation log to follow the established format used by `ai-conversations/copilot-task-11.md`.

## Prompt summary

The original task requested:

* An `AI_PROVIDER` setting with `ollama` as the default.
* Validation of `ollama` and `openai`, including case normalization.
* Environment-configurable Ollama URL, chat model, and embedding model.
* Preservation of existing OpenAI, ChromaDB, and application settings.
* Focused configuration tests.
* No runtime provider selection or unrelated file changes.
* A sequential conversation log containing the prompt, implementation, changed files, and test results.

A corrective prompt was subsequently sent to make the environment-variable mapping explicit, isolate configuration tests from the developer's environment, and bring this log into line with Task 11.

## Implementation / result

Added `ai_provider`, defaulting to `ollama`, with validation that trims surrounding whitespace, normalizes case, and accepts only `ollama` or `openai`.

Added the following Ollama settings with their requested defaults:

* `ollama_base_url`: `http://host.docker.internal:11434`
* `ollama_chat_model`: `llama3.2`
* `ollama_embedding_model`: `nomic-embed-text`

Existing OpenAI, ChromaDB, and application settings were preserved. Configuration tests were expanded to cover defaults, environment-variable loading, provider normalization, and invalid values.

## Files changed

* `backend/app/config.py`
* `backend/tests/test_config.py`
* `ai-conversations/copilot-task-12.md`

## Tests and result

The following results were reported for the original implementation:

* From `backend/`: `python -m pytest tests/test_config.py -q` - **5 passed**.
* From `backend/`: `python -m pytest tests -q` - **42 passed, 2 warnings**.

The two warnings were reported as existing Starlette/TestClient deprecation warnings.

The corrective run reported the same results:

* From `backend/`: `python -m pytest tests/test_config.py -q` - **5 passed**.
* From `backend/`: `python -m pytest tests -q` - **42 passed, 2 warnings**.

These are the results reported by Copilot; they have not been independently rerun as part of editing this log.

## Important decisions / assumptions

* `AI_PROVIDER` is explicitly mapped using Pydantic Settings' `validation_alias`.
* `ollama` is the default only when the environment variable is not set.
* Ollama configuration is read from `OLLAMA_BASE_URL`, `OLLAMA_CHAT_MODEL`, and `OLLAMA_EMBEDDING_MODEL`.
* Configuration support does not imply that runtime provider switching has been implemented.
* No provider clients, embedding logic, or RAG behavior were changed.

## Corrections / limitations

The corrective work explicitly mapped `AI_PROVIDER` and added an autouse fixture that clears recognized application-setting environment variables before each configuration test. Tests that require environment values set them explicitly.

The corrective prompt also required this log to retain both the original prompt and the corrective prompt, without creating a new task log.

**Corrective prompt given to Copilot:**
[Insert the exact corrective prompt sent to Copilot here, without reformatting or rewriting it.]

Runtime selection between Ollama and OpenAI remains outside the scope of Task 12 and must be implemented and tested in a subsequent task.
