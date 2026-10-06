# Enterprise Knowledge Base RAG Chatbot — Implementation Plan

## Goal

Build a small full-stack prototype of an enterprise RAG chatbot.

The application should allow Customer Success Managers to ask natural-language questions about internal product documentation and receive:

1. An answer generated strictly from the provided documentation.
2. Specific citations identifying the documents/chunks used.
3. A clear response when the answer cannot be found in the documentation.

The project must be easy to run locally and must be suitable for a technical interview where every implementation choice can be explained.

---

# Technology choices

## Backend

* Python 3.12+
* FastAPI
* Pydantic
* ChromaDB as the local vector store
* OpenAI API for embeddings and LLM
* pytest for tests

Do not introduce additional frameworks unless there is a clear reason.

## Frontend

* React
* Vite
* TypeScript
* Simple CSS

Do not spend significant effort on visual design.

## Infrastructure

* Docker
* Docker Compose
* Environment variables for configuration
* No paid API keys committed to the repository

## RAG

Use a straightforward RAG pipeline rather than an agent architecture.

Pipeline:

documents
→ document loading
→ chunking
→ embeddings
→ ChromaDB
→ similarity retrieval
→ prompt construction
→ LLM
→ answer + citations

Do not use LangGraph or multi-agent architecture.

---

# Target project structure

Create a clean structure similar to:

project-root/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── ingestion.py
│   │   ├── retrieval.py
│   │   ├── llm.py
│   │   └── rag.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   └── ...
│
├── data/
│   ├── authentication.md
│   ├── payments.md
│   ├── integrations.md
│   └── troubleshooting.md
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md

The exact structure may be adjusted if there is a strong technical reason.

---

# Mock knowledge base

Create 4 realistic enterprise documentation articles.

Suggested topics:

1. Authentication and OAuth configuration
2. Payment configuration
3. Third-party integrations
4. Troubleshooting common configuration issues

The documents should contain enough detail to demonstrate:

* simple retrieval
* retrieval from different documents
* multi-chunk answers
* questions with no answer

Each document should have useful metadata such as:

* document name
* title
* section
* chunk ID

---

# Functional requirements

## Document ingestion

The backend should:

1. Load the mock documentation.
2. Split documents into chunks.
3. Attach metadata to each chunk.
4. Generate embeddings.
5. Store chunks and embeddings in ChromaDB.

The ingestion process should be deterministic and easy to run locally.

---

# Retrieval

Given a user question:

1. Generate an embedding for the question.
2. Query ChromaDB.
3. Retrieve the most relevant chunks.
4. Preserve their metadata.
5. Pass the retrieved content to the LLM.

Use a configurable `top_k`, with a sensible default such as 3.

---

# LLM behavior

The LLM must be explicitly instructed:

* Use only the supplied documentation.
* Do not invent information.
* If the answer is not contained in the retrieved documentation, say that the information is not available.
* Do not use outside knowledge.
* Produce a concise answer.

The backend should keep the retrieved source metadata separately from the generated answer.

Do not ask the LLM to invent citation metadata.

---

# API

Implement at least:

## GET /health

Returns a simple health response.

Example:

{
"status": "ok"
}

## POST /chat

Request:

{
"question": "How do I configure OAuth?"
}

Response:

{
"answer": "...",
"sources": [
{
"document": "authentication.md",
"section": "OAuth Configuration",
"chunk_id": "..."
}
]
}

Use Pydantic models for request and response validation.

Validate empty or invalid questions.

---

# Frontend

Create a simple chat interface.

The user should be able to:

1. Enter a question.
2. Submit it.
3. See the assistant answer.
4. See the sources/citations used.
5. See an error if the backend request fails.
6. See a clear "information not found" response when appropriate.

The UI does not need authentication or persistent chat history.

Keep the implementation simple and readable.

---

# Tests

Create basic automated tests for:

1. Document chunking.
2. Metadata preservation.
3. Retrieval.
4. Health endpoint.
5. Chat endpoint.
6. Citation presence.
7. No-answer behavior.

Prefer unit tests for core logic and a small number of API tests.

Avoid unnecessary test complexity.

---

# Docker

Docker Compose should start the complete application.

The intended experience should be approximately:

docker compose up --build

The README must explain:

* prerequisites
* environment variables
* how to start the application
* frontend URL
* backend URL
* how to run tests
* how to provide the LLM API key

Never commit API keys.

Provide `.env.example`.

---

# Error handling

Handle at least:

* empty question
* invalid request
* missing API key
* LLM failure
* retrieval failure
* no relevant information

Errors should return useful HTTP responses without exposing secrets.

---

# README

The README should explain:

1. Problem statement
2. Architecture
3. RAG flow
4. Project structure
5. API design
6. Technology choices
7. Why ChromaDB was chosen
8. Chunking strategy
9. Retrieval strategy
10. Citation approach
11. Error handling
12. Local setup
13. Docker setup
14. Testing
15. Limitations
16. Possible production improvements
17. AI assistant usage

The README should explicitly distinguish prototype decisions from production recommendations.

---

# Operational / production discussion

The implementation is a prototype, but the README should briefly discuss how the system could evolve.

Possible future improvements:

* PostgreSQL + pgvector
* persistent document ingestion pipeline
* document versioning
* authentication/authorization
* observability and tracing
* structured logging
* rate limiting
* caching
* evaluation dataset for retrieval quality
* hybrid keyword + semantic search
* reranking
* asynchronous ingestion
* background jobs
* horizontal scaling
* secret management
* CI/CD

Do not implement these unless required for the prototype.

---

# AI assistant requirement

The assignment requires an export of AI assistant conversation logs.

Create a suitable location for the logs, for example:

docs/ai-assistant-log.md

The README must contain a short section describing:

* which AI assistants were used
* what they were used for
* that the submitted code was reviewed by the candidate

Do not claim that AI-generated code was blindly accepted.

---

# Development strategy

Implement the project incrementally.

Do NOT generate the entire application in one step.

Each implementation step should:

1. Make one small change.
2. Explain the files changed.
3. Run or suggest the relevant tests.
4. Stop and wait for verification before continuing.

Prioritize a working end-to-end MVP by the end of the third development day.

Keep days 4 and 5 as buffer for debugging, polish, documentation, and interview preparation.

---

# Definition of Done

The project is considered complete when:

* Documents can be ingested.
* Chunks are stored in ChromaDB.
* Questions retrieve relevant chunks.
* LLM answers are based only on retrieved documentation.
* Answers include source citations.
* Unknown questions receive a safe "not found" response.
* FastAPI exposes `/health` and `/chat`.
* React frontend can interact with `/chat`.
* Docker Compose starts the stack.
* Tests pass.
* README explains the architecture and trade-offs.
* No API keys are committed.
* AI assistant conversation logs are included.
* The candidate can explain every important architectural and implementation decision.

# Important constraint

Favor simplicity, readability, and explainability over unnecessary sophistication.

This is a Senior Software Engineer prototype, not a production-scale platform.

Do not add technologies or abstractions merely to make the project look more sophisticated.
