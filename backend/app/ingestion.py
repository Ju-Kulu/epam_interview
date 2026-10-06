"""Load Markdown knowledge-base documents from disk."""

from dataclasses import dataclass
from pathlib import Path


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class LoadedDocument:
    name: str
    title: str | None
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document: str
    title: str | None
    text: str


def _extract_title(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or None
    return None


def _markdown_files(data_dir: Path) -> list[Path]:
    return sorted(
        path for path in data_dir.glob("*.md") if path.name.lower() != "readme.md"
    )


def load_documents(data_dir: str | Path = DEFAULT_DATA_DIR) -> list[LoadedDocument]:
    """Load all knowledge-base Markdown files from ``data_dir``."""
    directory = Path(data_dir)
    if not directory.is_dir():
        raise FileNotFoundError(f"Knowledge-base data directory does not exist: {directory}")

    files = _markdown_files(directory)
    if not files:
        raise ValueError(f"No Markdown knowledge-base documents found in: {directory}")

    documents = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        documents.append(
            LoadedDocument(name=path.stem, title=_extract_title(text), text=text)
        )
    return documents


def _validate_chunk_parameters(chunk_size: int, overlap: int) -> None:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if overlap < 0:
        raise ValueError("overlap must be greater than or equal to 0.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")


def chunk_documents(
    documents: list[LoadedDocument], chunk_size: int = 500, overlap: int = 50
) -> list[DocumentChunk]:
    """Split documents into deterministic character-based chunks."""
    _validate_chunk_parameters(chunk_size, overlap)
    chunks = []
    step = chunk_size - overlap

    for document in documents:
        if not document.text.strip():
            continue

        start = 0
        chunk_index = 0
        while start < len(document.text):
            end = min(start + chunk_size, len(document.text))
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{document.name}-{chunk_index}",
                    document=document.name,
                    title=document.title,
                    text=document.text[start:end],
                )
            )
            if end == len(document.text):
                break
            start += step
            chunk_index += 1

    return chunks
