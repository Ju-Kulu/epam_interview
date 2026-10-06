"""Load Markdown knowledge-base documents from disk."""

from dataclasses import dataclass
from pathlib import Path


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class LoadedDocument:
    name: str
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
