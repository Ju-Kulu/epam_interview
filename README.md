# Enterprise Knowledge Base RAG Chatbot

A local full-stack Retrieval-Augmented Generation (RAG) prototype for OmniCorp Solutions Customer Success Managers (CSMs). Ask questions about four mock enterprise guides and inspect the source references and original Markdown used by the answer.

This repository describes a prototype, not a production-ready or authenticated knowledge service. The recommended setup is Docker Compose on Windows with Ollama running on the same Windows host. The backend can also select OpenAI, but that mode requires a valid API key and was not exercised in the local smoke test described below.

## 1. Project overview

The service loads Markdown documents from `data/` into a ChromaDB collection, retrieves the three nearest chunks for a question, and asks a configured chat model to answer from those chunks. The API returns the answer and source metadata. In the UI, selecting a source opens the original document content.

The repository contains four mock guides, not the hundreds of manuals in the assignment scenario. Results therefore demonstrate the pipeline but do not represent a production-sized corpus.

## 2. Problem statement and intended users

The intended users are CSMs who need to find configuration guidance without manually searching internal product manuals. This prototype shows how a small document collection can support grounded question answering and source inspection.

## 3. Implemented features

- Synchronous Markdown loading, H1 title extraction, and missing/empty-directory errors.
- Deterministic Markdown-aware chunking with paragraph, heading, sentence, and word-aware boundaries; configurable chunk size and overlap are function arguments in code.
- Ollama and OpenAI selection for chat and embeddings through `AI_PROVIDER`.
- ChromaDB HTTP client and persistent collection storage, with collection names separated by provider and embedding model.
- Startup indexing through FastAPI's lifespan. Starting/restarting the backend loads and embeds the current documents.
- Upsert of incoming chunks and stale-chunk removal for documents represented in that indexing batch.
- Similarity retrieval (`top_k=3` by default), grounded answer prompt, and source metadata preserved outside the model response.
- FastAPI `/health`, `/chat`, and `/documents/{document_id}` routes.
- React chat UI with loading/error feedback, returned source references, and a panel that loads original Markdown.
- Backend automated tests. No frontend unit-test framework is configured.

Not implemented: user authentication/authorization, document upload, an admin indexing endpoint, a retrieval relevance threshold, reranking, hybrid search, or production observability.

## 4. Architecture overview

```text
Browser
    -> Vite development server (port 5173)
        -> /chat and /documents proxy to FastAPI (backend:8000 in Compose)
                -> RAG orchestration
                    -> VectorStore embeds question and searches ChromaDB
                    -> configured chat provider receives retrieved text
                -> typed answer and source metadata returned to browser

FastAPI startup
    -> load /data Markdown
    -> chunk documents
    -> configured embedding provider
    -> ChromaDB HTTP service (chromadb:8000)
```

Compose starts `frontend`, `backend`, and `chromadb`. Ollama is deliberately external to Compose and normally runs as an Ollama service on the Windows host.

## 5. RAG pipeline and request/data flow

1. On backend startup, `index_knowledge_base()` calls the loader and chunker for Markdown files in `/data`.
2. The loader excludes `README.md`, extracts the first level-one heading as the title, and retains the complete file text.
3. The chunker preserves paragraph/Markdown boundaries where possible, groups headings with following content when they fit, then uses sentence and word-aware fallback splitting. Default calls use 500 characters and 50 characters of overlap.
4. The selected embedding provider embeds each chunk. ChromaDB stores its text, vector, deterministic ID, and `document`, `title`, and `chunk_id` metadata.
5. `POST /chat` sends the question to `answer_question()`. `VectorStore.search()` embeds it using the same provider/model as indexing and asks Chroma for the nearest three chunks.
6. The RAG layer puts only retrieved chunk text into the factual context supplied to the chat model. The prompt instructs the model not to invent facts and to say when the knowledge base lacks an answer.
7. The API returns the model answer plus source fields created from retrieved chunks, not from model-generated citations.
8. The UI displays the title/document, chunk ID, and Chroma distance. Clicking a source calls `/documents/{document_id}` and displays the original Markdown text.

The chat model generates language; the embedding model converts text into vectors used for similarity search. They are independently configured and are not interchangeable. Chroma distance is a retrieval metric, not a calibrated confidence or correctness score. The current search returns nearest results without a relevance threshold, reranker, or keyword/hybrid search. Source references help inspection but do not guarantee that an answer is correct or eliminate hallucinations.

## 6. Technology stack

- Backend image: Python 3.12 slim, FastAPI, Pydantic/Pydantic Settings, Uvicorn.
- Chat and embeddings: Ollama HTTP API by default; OpenAI SDK when `AI_PROVIDER=openai`.
- Vector store: ChromaDB 1.5.9 HTTP service.
- Frontend image: Node 20 Alpine, React 18, Vite 5, TypeScript 5.
- Tests: pytest; FastAPI `TestClient` and fake provider/vector-store clients.
- Infrastructure: Docker Compose.

ChromaDB was selected as a simple persistent vector store with metadata-aware records and nearest-neighbor query support for this local prototype. The current deployment is a single Compose stack, not a horizontally scaled or access-controlled vector service.

The Dockerfiles specify container runtimes. The repository does not declare a formal minimum host Docker Desktop, PowerShell, Python, or Node version. The audit machine used Docker 29.8.0 / Compose 5.5.1, Python 3.13.15, Node 24.19.0, npm 11.17.0, and Ollama 0.34.2; these are observed versions, not project minimums.

## 7. Repository structure

```text
backend/app/       Configuration, ingestion/chunking, indexing, vector store,
                                     provider integrations, RAG orchestration, API and schemas
backend/tests/     Backend unit and API tests
data/              Four mock Markdown knowledge-base guides
frontend/src/      React chat UI and CSS
docs/              General AI assistant note
ai-conversations/  Per-task summaries and raw prompt archive
docker-compose.yml Local Compose services and volumes
.env.example       Safe environment template
```

`backend/app/retrieval.py` is a placeholder; the active retrieval implementation is `VectorStore.search()` in `vector_store.py`.

## 8. Prerequisites

For the recommended Windows 10/11 setup:

- Git for cloning the repository.
- Docker Desktop configured to run Linux containers, with Docker Compose available.
- Ollama on the Windows host for the default provider. Ollama is not a Compose service.
- Network access to download Docker images and Ollama model files.
- Enough free disk space and memory for Docker images and both models. Model sizes/resource use vary by Ollama release and platform.

Python and Node.js are not required on the host for the Compose setup. They are needed if running backend tests or the frontend tooling directly on Windows. The backend Docker image uses Python 3.12; the frontend Docker image uses Node 20.

Check tools in a Windows PowerShell terminal:

```powershell
git --version
docker --version
docker compose version
ollama --version
docker info
```

`docker info` should return server information. If it fails, start Docker Desktop and wait until its engine is ready. `ollama --version` only confirms installation; later steps check the running Ollama API and models.

## 9. Configuration reference

Settings are read by Pydantic Settings from environment variables. Compose reads the root `.env` through `env_file`; do not commit `.env` (it is ignored by `.gitignore`). `.env.example` contains placeholders and local defaults, not credentials. The Ollama variables below are optional in the file because the application supplies defaults.

| Variable | Default / required | Purpose and notes |
|---|---|---|
| `APP_NAME` | `enterprise-kb-rag-chatbot`; optional | Present in `Settings`; currently the FastAPI title is a fixed string, so changing this value does not rename the API. |
| `APP_ENV` | `development`; optional | Stored in settings; no environment-specific behavior currently branches on it. |
| `BACKEND_HOST` | `0.0.0.0`; optional | Passed into the backend container, but the Dockerfile's Uvicorn command explicitly binds `0.0.0.0`. |
| `BACKEND_PORT` | `8000`; optional | Passed into the container; Uvicorn and Compose port mapping are currently fixed to 8000. |
| `AI_PROVIDER` | `ollama`; optional | Selects `ollama` or `openai` for both chat and embeddings. Values are normalized to lowercase. |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434`; optional | Base URL used by the backend container to reach Ollama on Docker Desktop's Windows host. Set this when Ollama is elsewhere. |
| `OLLAMA_CHAT_MODEL` | `llama3.2`; optional | Ollama model for answer generation. Pull this model before the first indexing/chat startup. |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text`; optional | Ollama model for document and question vectors. Changing it selects another Chroma collection and requires startup reindexing. |
| `OPENAI_API_KEY` | unset in application settings; required only for `AI_PROVIDER=openai` | Secret for the OpenAI SDK. Put a real key only in ignored `.env` or a secret manager; never commit it. Not needed in Ollama mode. |
| `OPENAI_MODEL` | `gpt-4o-mini`; optional in Ollama mode | OpenAI chat model. Used only when provider is OpenAI. |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small`; optional in Ollama mode | OpenAI embedding model. Used only when provider is OpenAI; changing it selects a separate collection. |
| `CHROMA_HOST` | `localhost`; optional local default | Chroma server host. Compose overrides the backend container value to `chromadb`. |
| `CHROMA_PORT` | `8001`; optional local default | Chroma host port. Compose overrides the backend container value to `8000`, Chroma's internal port. Host access remains `localhost:8001`. |
| `CHROMA_COLLECTION` | `knowledge_base`; optional | Base collection name. The vector store adds provider/model identity to the actual collection name. |
| `VITE_API_PROXY_TARGET` | `http://localhost:8000` in `.env.example` | Vite proxy target for `/chat` and `/documents`. Compose explicitly overrides it to `http://backend:8000`; changing the root `.env` value does not change Compose's frontend target. |
| `FRONTEND_PORT` | `5173` in `.env.example` | Currently not consumed by Compose or Vite configuration; the host mapping and Vite port are fixed at 5173. |

There is no configurable data-directory variable: the backend uses `/data`, which Compose mounts from `./data` read-only.

For OpenAI mode, set `AI_PROVIDER=openai` and replace the placeholder `OPENAI_API_KEY` with a valid key. The backend provider implementations exist, but this README audit's live request used Ollama; OpenAI connectivity was not tested.

## 10. Recommended setup: Docker Compose with Ollama

These steps target a fresh Windows clone and run commands in a host PowerShell terminal unless stated otherwise.

### Clone and configure

```powershell
git clone https://github.com/Ju-Kulu/epam_interview.git
Set-Location .\epam_interview
Copy-Item .env.example .env
```

`Copy-Item` creates Compose's required `.env` file. For default Ollama use, the defaults can remain; the sample OpenAI key is only a placeholder and is not used by Ollama. Review the provider/model and local Chroma values in `.env`. Do not paste a real key into source control.

### Start Ollama and download models

Ollama runs on Windows, outside Docker Compose. The installer normally runs it as a background service. If it is not running, open a separate PowerShell window and run:

```powershell
ollama serve
```

Keep that window open if you started the process manually. In another host PowerShell window:

```powershell
ollama pull llama3.2
ollama pull nomic-embed-text
ollama list
Invoke-RestMethod -Uri http://localhost:11434/api/tags |
        ConvertTo-Json -Depth 4
```

Successful verification lists `llama3.2` and `nomic-embed-text` (often with `:latest`). If a model is absent, repeat its `ollama pull` command. If the API request fails, confirm Ollama is running and listening on port 11434.

### Build and start the application

From the repository root, first validate Compose, then build and start all three services:

```powershell
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

`config --quiet` should exit successfully without output. `up --build -d` builds backend/frontend images and starts `backend`, `frontend`, and `chromadb` in the background. `depends_on` orders startup but does not wait for Chroma readiness, and Ollama is external; check backend logs if startup indexing fails:

```powershell
docker compose logs --tail 100 backend
docker compose logs --tail 100 chromadb
```

The backend only becomes available after lifespan startup indexing completes. A ready state in `docker compose ps` plus successful `/health` and `/chat` calls below are stronger checks than simply seeing that containers were created. The health endpoint itself does not actively probe downstream dependencies after startup.

Open the chat UI at <http://localhost:5173/>. The backend is published at <http://localhost:8000/>; interactive API docs are at <http://localhost:8000/docs>. ChromaDB is published on host port 8001 for local diagnostics; it is not authenticated and should not be exposed to untrusted networks.

## 11. Local setup without Docker

**A full host-only backend setup is not supported as-is.** `load_documents()` defaults to `/data`, and the application lifespan does not provide a host data-directory override. ChromaDB is configured as an HTTP service, so a Chroma server must also be running. On Windows, a fresh checkout does not provide the `/data` mount that Compose supplies.

You can run backend unit tests on the host (see section 17). You can also run the frontend dev server on the host while keeping the Docker backend/Chroma running:

```powershell
Set-Location .\frontend
npm install
$env:VITE_API_PROXY_TARGET = 'http://localhost:8000'
npm run dev
```

Then open <http://localhost:5173/>. This hybrid setup uses host Node/npm for Vite and the Compose backend for API/data access. Do not use `http://backend:8000` from a host browser; that service name resolves only on the Compose network.

Running the complete backend directly on Windows would require arranging a `/data` directory and reachable Chroma service (and keeping those paths/services consistent with startup indexing). That flow has not been implemented or verified; no host-only backend command is presented as supported.

## 12. Local versus remote Ollama configuration

### Scenario A - application in Docker, Ollama on the same Windows host (recommended)

The configured default `http://host.docker.internal:11434` is the Docker Desktop host gateway. In the current running stack, a request from inside the backend container to that URL's `/api/tags` endpoint succeeded and listed both configured models. The corresponding host check is:

```powershell
Invoke-RestMethod -Uri http://localhost:11434/api/tags |
        Select-Object -ExpandProperty models |
        Select-Object -ExpandProperty name
```

If the default is unsuitable, set `OLLAMA_BASE_URL` in root `.env`; Compose's `env_file` passes it into the backend. To test from the container:

```powershell
docker compose exec backend python -c "import httpx; r=httpx.get('http://host.docker.internal:11434/api/tags', timeout=5); r.raise_for_status(); print([m['name'] for m in r.json()['models']])"
```

This uses HTTP on the local Docker Desktop network. Do not expose the Ollama port publicly.

### Scenario B - backend and frontend both directly on Windows

**Not supported end-to-end by the current checkout.** The frontend can run directly as shown in section 11 when the backend is available, but direct backend startup defaults to `/data`; there is no application setting to point indexing at the repository's `data/` path. Also, the direct backend needs a running Chroma HTTP service. A code/configuration change would be needed to make a fresh host-only backend setup reliable.

### Scenario C - Ollama on another machine

The backend accepts a configurable `OLLAMA_BASE_URL`, so using a private, reachable Ollama host is supported by configuration but was not tested here. Put a URL reachable **from the backend container** in root `.env`, for example:

```dotenv
OLLAMA_BASE_URL=http://192.168.1.40:11434
```

Use the actual private address and port for your network. Check the URL from the host and from the backend container with `/api/tags`; a host-only successful check does not prove the Compose container can reach it. Permit traffic only between trusted machines/networks. Ollama's default endpoint does not provide application-level authentication in this project; do not expose it directly to the public internet. HTTPS, authentication, and certificate configuration for remote Ollama are not implemented or verified here.

## 13. Running on a remote Linux server

Remote Linux deployment is **configurable but unverified**. Compose publishes ports 5173, 8000, and 8001 on all host interfaces by default, and the Vite service is a development server. Do not leave those ports publicly reachable.

Ollama placement options:

- **Ollama on another private machine:** set `OLLAMA_BASE_URL` to its private DNS name/IP as reachable from the backend container.
- **Ollama on the Docker host:** the Windows/Docker Desktop default `host.docker.internal` is not configured by this Compose file for native Linux. Use a reachable host/gateway address, or add and verify a Linux-specific host-gateway mapping in a separately reviewed Compose change. The latter is not part of this README task.
- **Ollama in another container:** this Compose file does not define an Ollama service. A network/service configuration change would be required.

If Ollama runs on the Linux host, it must listen on an interface reachable from the Docker bridge; its default loopback-only listener may not be reachable from containers. Binding to a network interface can expose an unauthenticated endpoint, so restrict access with host/network firewall rules to the backend host or private network. Do not bind it to a public interface without a secured proxy and appropriate authentication controls.

For a temporary browser session, an administrator can restrict inbound firewall access to trusted sources and use an SSH tunnel from the developer's machine:

```powershell
ssh -N -L 5173:127.0.0.1:5173 user@your-server
```

With the tunnel running, open <http://localhost:5173/> locally. The frontend's `/chat` and `/documents` proxy remains inside the Compose network. The SSH tunnel alone does not secure the server's other published ports; firewall rules must separately restrict ports 8000 and 8001 (and 5173 except as intended). For sustained deployment, use a reviewed TLS reverse proxy, access controls, and a production frontend build/server. Those deployment changes are not included or tested here.

## 14. Starting, stopping, restarting and rebuilding

Run these commands from the repository root:

```powershell
docker compose up -d                 # Start existing images/services
docker compose up --build -d         # Rebuild changed images, then start
docker compose restart backend       # Restart backend; startup indexing runs again
docker compose up -d --force-recreate backend # Recreate backend to apply changed .env values
docker compose logs -f backend       # Follow backend startup/request logs
docker compose logs -f frontend      # Follow Vite logs
docker compose logs -f chromadb      # Follow ChromaDB logs
docker compose ps                    # Show service state and published ports
docker compose down                  # Stop/remove containers and network; keep named volumes
```

Restarting reuses existing containers/images and reruns backend startup indexing. Rebuilding recreates an image from its Dockerfile and build context; it does not itself erase `chroma_data`. `docker compose down` keeps named volumes. **Do not use `docker compose down -v` as routine troubleshooting:** `-v` removes named volumes, including persisted ChromaDB data and the frontend dependency volume.

## 15. Verifying the installation

From host PowerShell after startup:

```powershell
docker compose ps
Invoke-RestMethod -Uri http://localhost:8000/health
Invoke-WebRequest -Uri http://localhost:5173/ -UseBasicParsing
```

The API should return `{"status":"healthy"}` and the frontend request should return HTTP 200. This confirms processes/routes respond, not that the corpus was retrieved correctly. The app has no dedicated readiness or indexing-status endpoint.

Check mounted document loading from inside the backend container:

```powershell
docker compose exec backend python -c "from app.ingestion import load_documents, chunk_documents; docs=load_documents(); chunks=chunk_documents(docs); print('documents:', len(docs), 'chunks:', len(chunks))"
```

Then submit a question and inspect its answer/sources using the example in section 16. A nonempty `sources` array is evidence that retrieval returned chunks; assess the source content rather than treating an HTTP 200 alone as proof of answer quality.

## 16. API endpoints and example requests

FastAPI's interactive Swagger UI is available at `/docs`; its OpenAPI schema is at `/openapi.json`.

| Method | Path | Purpose and response |
|---|---|---|
| `GET` | `/health` | Returns `{"status":"healthy"}`. It is a simple process/app response, not a continuous downstream health probe. |
| `POST` | `/chat` | Accepts `{"question":"..."}` and returns `answer` plus `sources` containing `chunk_id`, `document`, nullable `title`, and `distance`. Empty/whitespace questions and invalid bodies receive FastAPI/Pydantic HTTP 422 validation responses. |
| `GET` | `/documents/{document_id}` | Returns `document`, `title`, and the full original Markdown `content`; unknown IDs return HTTP 404. IDs are filename stems such as `authentication`, without `.md`. |

PowerShell chat example (uses the running local Ollama configuration by default):

```powershell
$body = @{ question = 'What should OAuth redirect URLs use?' } | ConvertTo-Json
$result = Invoke-RestMethod `
        -Method Post `
        -Uri 'http://localhost:8000/chat' `
        -ContentType 'application/json' `
        -Body $body
$result.answer
$result.sources | Format-Table chunk_id, document, title, distance
```

The same endpoint can be sent through the frontend proxy at `http://localhost:5173/chat`. To inspect a source directly:

```powershell
$source = Invoke-RestMethod -Uri 'http://localhost:8000/documents/authentication'
$source.title
$source.content
```

The UI makes this document request when a source title is clicked. Chat/provider failures use FastAPI's normal server error handling; there is no custom error schema for upstream provider failures.

## 17. Automated tests

Backend tests are under `backend/tests/`. They cover configuration, loading/chunking, indexing orchestration, provider adapters with fake clients, RAG orchestration, and API routes with dependency overrides. They do not require a live model or Chroma service.

On Windows, from the repository root, create a host test environment if needed:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Set-Location .\backend
python -m pytest tests -q
```

If Python 3.12 is not installed, use the Python version installed on the host that is compatible with the pinned packages; the backend image itself uses Python 3.12. Alternatively run tests from the backend container:

```powershell
docker compose exec backend python -m pytest tests -q
```

Frontend has no configured unit-test script/framework. Its available scripts are `npm run dev`, `npm run build`, and `npm run preview`; run a production compile/build from `frontend/` with `npm run build`.

## 18. Logs and troubleshooting

| Symptom | Checks and safe next steps |
|---|---|
| Docker is unavailable | Start Docker Desktop, wait for its engine, then retry `docker info` and `docker compose ps`. |
| A port is occupied | Inspect `docker compose ps` and use Windows `Get-NetTCPConnection -LocalPort 5173,8000,8001`; stop the conflicting process or deliberately change the Compose mapping and matching URLs. The current ports are fixed in Compose. |
| Ollama is not running/model missing | Run `ollama list`; check `Invoke-RestMethod http://localhost:11434/api/tags`; start Ollama and pull `llama3.2` and `nomic-embed-text`. |
| Backend cannot reach Ollama | Test `/api/tags` from inside the backend container (section 12). Confirm `OLLAMA_BASE_URL`, host firewall, listener interface, and port 11434. Host success alone is insufficient. |
| Backend cannot reach Chroma | Check `docker compose logs chromadb`; inside the Compose network the configured address must be `chromadb:8000`, not host port 8001. `depends_on` does not wait for Chroma readiness. |
| Frontend cannot reach backend | Check frontend logs and confirm Compose sets `VITE_API_PROXY_TARGET=http://backend:8000`. In host-run Vite mode, use `http://localhost:8000`; Compose service names do not resolve on Windows. |
| Backend keeps restarting during indexing | Read `docker compose logs --tail 200 backend`. Confirm Ollama and Chroma are reachable and `/data` contains the Markdown files. Startup indexing occurs before request serving. |
| Chat returns 422 | Send JSON with a non-empty string `question`; inspect the response's `detail` field. |
| Chat returns a server error | Inspect backend logs for provider, model, Chroma, or embedding errors. Confirm provider variables and model availability. Do not paste secrets into logs/issues. |
| Vite serves a blank/stale page | Inspect frontend logs and browser developer console; verify `npm run build` if editing locally. Restart/rebuild only the relevant service after code changes. |
| Results are stale after data/model changes | Restart backend to rerun indexing. Check collection/model settings and see section 19. Do not delete the Chroma volume as a first response. |

## 19. Data persistence and document re-indexing

- Original Markdown lives in host `data/` and is mounted read-only at `/data` in the backend.
- ChromaDB data lives in the named `chroma_data` volume mounted at `/data` inside the Chroma container. It survives ordinary container restarts/recreation unless the volume is explicitly removed.
- `frontend_node_modules` is a separate named volume used for the frontend dependency mount.
- Ollama model files are managed by the Ollama installation on its host/server and are outside these Compose volumes.
- The backend creates its provider/model-specific collection automatically when `VectorStore` starts.
- Indexing runs on every backend application startup and re-embeds the current corpus. There is no admin reindex endpoint or separate CLI command.
- Reindexing upserts current deterministic IDs, then removes stale chunks for each document represented in that indexing batch. A document removed entirely from `data/` is not represented in the new batch, so its old records are not automatically deleted. A document that yields no chunks also has no IDs to trigger cleanup.
- Switching provider or embedding model selects a distinct collection. Current documents are indexed into it at backend startup; previous collections/data are retained and are not automatically migrated or deleted.
- Reindexing can make startup slow and requires Ollama/OpenAI plus Chroma to be available before the app finishes startup.

If deliberate data removal is required, first back up or verify the named volume and understand the loss. `docker compose down -v` removes persisted named volumes and is destructive; it is not a routine reindex command.

## 20. Security considerations

- `.env` is ignored by Git; keep real OpenAI keys there for local use and never commit them. The sample value in `.env.example` is a placeholder.
- Ollama mode does not require an OpenAI key. OpenAI mode does.
- The API has no user authentication, authorization, rate limiting, or tenant isolation. Do not place sensitive/private documents behind it as a public service.
- Compose publishes backend 8000, frontend 5173, and Chroma 8001 on host interfaces. Chroma and Ollama are not protected by application authentication here. Restrict firewall access to trusted local/private users.
- Ollama may accept unauthenticated requests on its listening interface. Do not expose it directly to the public internet.
- The default Compose frontend is Vite's development server, not a production-hardened web server. Use a separately secured deployment design for external access.
- Prompt constraints and citations are not security boundaries or guarantees of factual correctness.

## 21. Known limitations and future improvements

- Four mock documents only; no document management/upload or corpus synchronization service.
- Similarity retrieval returns top-k nearest chunks without a relevance threshold, reranking, hybrid/keyword search, or evaluation loop.
- No auth/access control, rate limiting, structured operational telemetry, or production deployment configuration.
- The simple `/health` route is not a separate readiness/dependency health system.
- Startup re-embeds documents on every backend start; deleted whole documents leave old records in the collection.
- Direct host-only backend setup is blocked by the fixed `/data` default and external Chroma requirement.
- Remote Ollama and native Linux host networking are configurable but unverified.
- The placeholder `backend/app/retrieval.py` is not used by the active search flow.
- The original assignment requests an export of assistant conversations. This repository has per-task summaries and a raw prompt archive, not a complete assistant transcript export; confirm with the reviewer whether those logs meet the requirement.

Possible follow-up work, outside this prototype, includes configurable data paths, readiness checks, incremental ingestion, cleanup for removed documents, retrieval evaluation/reranking, auth/access control, production frontend serving, and deployment-specific network/security configuration.

## 22. AI assistant usage logs

GitHub Copilot was used for incremental planning, implementation assistance, and test/documentation work. `ai-conversations/` contains per-task summaries and `raw_prompts.md` contains archived prompts. The project also has `docs/ai-assistant-log.md`, an earlier general note. The candidate should review and understand submitted code; these task summaries are not a full assistant transcript export.
