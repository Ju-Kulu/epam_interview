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
