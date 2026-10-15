# Task 17 - README Documentation Audit and Setup Guide

## Task name and goal
Audit and rewrite the README so a new developer can understand the implemented RAG application, configure and run the verified local setup, test it, troubleshoot it, and distinguish supported behavior from limitations.

## Prompt summary
Inspect the implementation, configuration, Compose setup, documents, tests, assignment specification, planning notes, and prior AI logs. Rewrite only the README with a practical Windows/Docker Desktop guide, provider and networking scenarios, API/test instructions, persistence/security details, and factual gaps. Create this task log in the required seven-section format; do not change application, environment, or Docker files.

## Implementation / result
Replaced obsolete scaffold instructions with a 22-section implementation-based guide. It documents the Windows Docker Desktop + host Ollama path, the real `/data` mount and startup indexing, provider/model settings, Vite proxy, API routes and clickable original-document flow, Chroma persistence/reindexing, PowerShell examples, troubleshooting, and security. It labels host-only backend execution and native-Linux/remote deployment as unsupported or unverified, and notes that the repository has task summaries/raw prompts rather than a full assistant transcript export.

Audited configuration and code including `docker-compose.yml`, `.env.example`, `.gitignore`, backend app/tests, frontend source/scripts/Vite config, all data Markdown files, `docs/`, `plan.md`, the original assignment, and Tasks 11–16 logs. `.env` was confirmed present but its contents were not opened or copied.

## Files changed
- `README.md` — rewritten setup, architecture, configuration, API, operations, verification, and limitations guide.
- `ai-conversations/copilot-task-17.md` — this audit record.

## Tests and result
- From `backend/`, `python -m pytest tests -q` — **70 passed, 2 warnings** (existing Starlette/TestClient deprecations).
- From `frontend/`, `npm run build` — **passed**; TypeScript and Vite production build completed.
- `docker compose -f 'D:\EPAM\epam_interview\docker-compose.yml' config --quiet` — **passed**, no output.
- PowerShell parser check over README fenced PowerShell examples — **17 blocks parsed, 0 errors**.
- README path audit — **27 paths checked, 0 missing**; 22/22 numbered sections present; no secret-like API key value found.
- Live local smoke checks on the already-running stack: `/health` returned `{"status":"healthy"}`; `/chat` through the frontend proxy returned an answer and 3 sources; `/documents/authentication` returned the original document (628 characters); frontend `/` returned HTTP 200. From the backend container, Ollama `/api/tags` listed `nomic-embed-text:latest` and `llama3.2:latest`, and Chroma heartbeat succeeded at `chromadb:8000`.

These checks used the existing running local environment, not a fresh clone/rebuild. OpenAI mode, remote Ollama, and remote Linux deployment were not tested.

## Important decisions / assumptions
- Docker Compose is the only verified full-stack setup: `frontend`, `backend`, and `chromadb`; Ollama runs outside Compose. The recommended Windows URL is the configured Docker Desktop host gateway `http://host.docker.internal:11434`.
- The README distinguishes local Chroma defaults (`localhost:8001`) from the backend container address (`chromadb:8000`), and documents settings that exist but do not currently control fixed Compose/Uvicorn ports.
- Full host-only backend instructions were not presented because ingestion defaults to `/data` and there is no data-path setting. Host Vite can proxy to the Compose backend.
- The health route is described as a simple app response, not a continuous dependency readiness check. Similarity distance is not represented as confidence.
- The frontend build generated TypeScript/Vite artifacts; those validation artifacts were removed. The existing untracked `backend/chroma_data/` directory was left untouched.

## Corrections / limitations
The README identifies that startup re-embeds the corpus, provider/model changes select another collection, and old collections are retained. Stale cleanup applies only to documents present in an indexing batch; completely removed documents or documents yielding no chunks can leave old vectors. Compose has no health checks and `depends_on` does not wait for Chroma readiness. The Compose frontend is Vite's development server, and published ports bind to host interfaces; remote use needs firewall and deployment controls.

The project contains four mock guides, and `data/README.md` remains placeholder text. `backend/app/retrieval.py` is also a placeholder; active retrieval is in `VectorStore.search()`. The original assignment's mandatory conversation export may not be fully satisfied by the repository's task summaries and raw prompts. A pre-existing untracked `backend/chroma_data/` directory was observed and not modified. No application, `.env`, frontend, or Docker configuration files were changed.
