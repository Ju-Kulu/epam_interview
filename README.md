# Enterprise Knowledge Base RAG Chatbot

This repository is intentionally scaffolded as an initial project foundation for a full-stack RAG chatbot prototype.

## Current status

This branch contains the project structure and configuration only. The application logic, retrieval pipeline, API routes, and interactive frontend behavior will be added in later implementation steps.

## Planned architecture

- Backend: Python + FastAPI + Pydantic
- Frontend: React + Vite + TypeScript
- Vector store: ChromaDB
- LLM: OpenAI-compatible API via environment variables
- Containerization: Docker + Docker Compose

## Project structure

- backend/ — Python service configuration and application package scaffolding
- frontend/ — React frontend configuration and app shell
- data/ — mock enterprise knowledge base documents
- docs/ — project documentation and AI assistant log
- docker-compose.yml — local stack orchestration
- .env.example — environment variable template

## Local setup

1. Copy .env.example to .env
2. Fill in the required values for your environment
3. Run docker compose up --build

## Frontend and backend URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## Notes

- No real API keys are committed to the repository.
- The app is designed as a prototype and will evolve in incremental steps.
- AI assistant usage and reviews are documented in the project log under ai-conversations/ai-assistant-log.md.

## AI Assistant Usage Logs

`ai-conversations/` contains concise per-task AI assistant usage logs for Tasks 1–4, including prompt summaries where exact historical text is unavailable, implementation results, changed files, test outcomes, and key decisions. This directory fulfills the assignment's AI assistant log requirement.

## Local Ollama Setup

The default AI provider is Ollama. Before running the application locally, make sure Ollama is installed and running.

Download the chat and embedding models:

```powershell
ollama pull llama3.2
ollama pull nomic-embed-text
```

Verify that both models are available:

```powershell
ollama list
```

The application uses:

* `llama3.2` for chat responses.
* `nomic-embed-text` for document embeddings and query embeddings.

The default Ollama URL is `http://host.docker.internal:11434` when the backend runs in Docker Compose. If running the backend directly on Windows, configure `OLLAMA_BASE_URL` to `http://localhost:11434`.

If you change the embedding provider or model, the documents must be re-indexed into the corresponding ChromaDB collection. Existing collections are not automatically deleted.
