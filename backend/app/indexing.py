"""Orchestrate loading, chunking, and indexing the knowledge base."""

from pathlib import Path

from app.ingestion import DocumentChunk, chunk_documents, load_documents
from app.vector_store import VectorStore


def index_knowledge_base(
    data_dir: str | Path | None = None,
    vector_store: VectorStore | None = None, # this is a hint, so our test with fake vector store passes
) -> int:
    
    """Load and chunk knowledge-base documents, then index the resulting chunks."""
    documents = load_documents() if data_dir is None else load_documents(data_dir)
    chunks: list[DocumentChunk] = chunk_documents(documents)
    store = vector_store if vector_store is not None else VectorStore()
    store.index_chunks(chunks)
    return len(chunks)