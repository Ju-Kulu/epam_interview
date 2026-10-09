"""Load Markdown knowledge-base documents from disk."""

from dataclasses import dataclass
from pathlib import Path
import re


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


_MARKDOWN_BLOCK_START = re.compile(
    r"(?m)^[ \t]{0,3}(?:#{1,6}[ \t]+|[-*+][ \t]+|\d+[.)][ \t]+|>[ \t]?)"
)
_PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n+")
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])(?=\s+)")


def _markdown_block_spans(text: str) -> list[tuple[int, int]]:
    boundaries = {0, len(text)}
    boundaries.update(match.end() for match in _PARAGRAPH_BREAK.finditer(text))
    boundaries.update(
        match.start()
        for match in _MARKDOWN_BLOCK_START.finditer(text)
        if match.start() > 0
    )

    ordered_boundaries = sorted(boundaries)
    return [
        (start, end)
        for start, end in zip(ordered_boundaries, ordered_boundaries[1:])
        if text[start:end].strip()
    ]


def _split_long_span(
    text: str, start: int, end: int, chunk_size: int
) -> list[tuple[int, int]]:
    spans = []
    while end - start > chunk_size:
        limit = start + chunk_size
        space = text.rfind(" ", start, limit)
        newline = text.rfind("\n", start, limit)
        boundary = max(space, newline)
        split_at = boundary + 1 if boundary > start else limit
        spans.append((start, split_at))
        start = split_at
    if start < end:
        spans.append((start, end))
    return spans


def _document_chunk_spans(text: str, chunk_size: int) -> list[tuple[int, int]]:
    spans = []
    for block_start, block_end in _markdown_block_spans(text):
        if block_end - block_start <= chunk_size:
            spans.append((block_start, block_end))
            continue

        sentence_boundaries = [
            block_start + match.start()
            for match in _SENTENCE_BREAK.finditer(text[block_start:block_end])
        ]
        sentence_points = [block_start, *sentence_boundaries, block_end]
        for sentence_start, sentence_end in zip(sentence_points, sentence_points[1:]):
            if sentence_end - sentence_start <= chunk_size:
                if text[sentence_start:sentence_end].strip():
                    spans.append((sentence_start, sentence_end))
            else:
                spans.extend(
                    span
                    for span in _split_long_span(
                        text, sentence_start, sentence_end, chunk_size
                    )
                    if text[span[0] : span[1]].strip()
                )
    return spans


def _pack_chunk_spans(
    text: str,
    spans: list[tuple[int, int]],
    chunk_size: int,
    overlap: int,
) -> list[str]:
    packed = []
    start_index = 0

    while start_index < len(spans):
        end_index = start_index
        while (
            end_index < len(spans)
            and spans[end_index][1] - spans[start_index][0] <= chunk_size
        ):
            end_index += 1

        chunk_start = spans[start_index][0]
        chunk_end = spans[end_index - 1][1]
        chunk_text = text[chunk_start:chunk_end].strip()
        if chunk_text:
            packed.append(chunk_text)

        if end_index == len(spans):
            break

        next_start = end_index
        if overlap:
            earliest_start = chunk_end - overlap
            next_new_end = spans[end_index][1]
            for candidate in range(start_index + 1, end_index):
                candidate_start = spans[candidate][0]
                if (
                    candidate_start >= earliest_start
                    and next_new_end - candidate_start <= chunk_size
                ):
                    next_start = candidate
                    break
        start_index = next_start

    return packed


def chunk_documents(
    documents: list[LoadedDocument], chunk_size: int = 500, overlap: int = 50
) -> list[DocumentChunk]:
    """Split documents at Markdown and sentence boundaries where possible."""
    _validate_chunk_parameters(chunk_size, overlap)
    chunks = []

    for document in documents:
        if not document.text.strip():
            continue

        spans = _document_chunk_spans(document.text, chunk_size)
        chunk_texts = _pack_chunk_spans(document.text, spans, chunk_size, overlap)
        for chunk_index, chunk_text in enumerate(chunk_texts):
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{document.name}-{chunk_index}",
                    document=document.name,
                    title=document.title,
                    text=chunk_text,
                )
            )

    return chunks
