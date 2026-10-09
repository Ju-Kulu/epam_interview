import pytest

from app.ingestion import DocumentChunk, LoadedDocument, chunk_documents, load_documents


def test_loads_all_markdown_documents_and_preserves_content(tmp_path):
    expected_documents = {
        "authentication": "# Authentication\nOAuth setup details.\n",
        "payments": "# Payments\nBilling configuration details.\n",
        "integrations": "# Integrations\nConnector configuration details.\n",
        "troubleshooting": "# Troubleshooting\nResolution steps.\n",
    }
    for name, text in expected_documents.items():
        (tmp_path / f"{name}.md").write_text(text, encoding="utf-8")
    (tmp_path / "README.md").write_text("# Folder notes\n", encoding="utf-8")

    documents = load_documents(tmp_path)

    assert {document.name for document in documents} == set(expected_documents)
    assert {document.title for document in documents} == {
        "Authentication",
        "Payments",
        "Integrations",
        "Troubleshooting",
    }
    assert {document.name: document.text for document in documents} == expected_documents
    assert all(document.text.strip() for document in documents)


def test_missing_data_directory_raises_clear_error(tmp_path):
    missing_directory = tmp_path / "missing"

    with pytest.raises(FileNotFoundError, match="data directory does not exist"):
        load_documents(missing_directory)


def test_empty_data_directory_raises_clear_error(tmp_path):
    with pytest.raises(ValueError, match="No Markdown knowledge-base documents found"):
        load_documents(tmp_path)


def test_short_document_produces_one_chunk():
    document = LoadedDocument(name="authentication", title="Authentication", text="OAuth")

    chunks = chunk_documents([document], chunk_size=10, overlap=2)

    assert chunks == [
        DocumentChunk(
            chunk_id="authentication-0",
            document="authentication",
            title="Authentication",
            text="OAuth",
        )
    ]


def test_long_document_produces_chunks_with_preserved_metadata_and_ids():
    document = LoadedDocument(
        name="payments",
        title="Payment Guide",
        text="First paragraph has useful facts.\n\nSecond paragraph has more facts.",
    )

    chunks = chunk_documents([document], chunk_size=40, overlap=0)

    assert [chunk.text for chunk in chunks] == [
        "First paragraph has useful facts.",
        "Second paragraph has more facts.",
    ]
    assert [chunk.chunk_id for chunk in chunks] == [
        "payments-0",
        "payments-1",
    ]
    assert all(chunk.document == "payments" for chunk in chunks)
    assert all(chunk.title == "Payment Guide" for chunk in chunks)
    assert chunk_documents([document], chunk_size=40, overlap=0) == chunks
    assert all(len(chunk.text) <= 40 for chunk in chunks)


def test_chunks_prefer_paragraph_boundaries():
    text = "Alpha paragraph with details.\n\nBeta paragraph with details."
    chunks = chunk_documents(
        [LoadedDocument(name="guide", title=None, text=text)],
        chunk_size=34,
        overlap=0,
    )

    assert [chunk.text for chunk in chunks] == [
        "Alpha paragraph with details.",
        "Beta paragraph with details.",
    ]


def test_oversized_paragraph_splits_at_sentence_boundaries():
    text = "First sentence has enough words. Second sentence has enough words."
    chunks = chunk_documents(
        [LoadedDocument(name="guide", title=None, text=text)],
        chunk_size=36,
        overlap=0,
    )

    assert [chunk.text for chunk in chunks] == [
        "First sentence has enough words.",
        "Second sentence has enough words.",
    ]


def test_oversized_sentence_uses_word_aware_character_fallback():
    text = "A very long sentence without a nearby stopping point"
    chunks = chunk_documents(
        [LoadedDocument(name="guide", title=None, text=text)],
        chunk_size=15,
        overlap=0,
    )

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 15 for chunk in chunks)
    assert all(not chunk.text.startswith(" ") for chunk in chunks)
    assert all(not chunk.text.endswith(" ") for chunk in chunks)
    assert "".join(chunk.text for chunk in chunks).replace(" ", "") == text.replace(" ", "")


def test_long_token_uses_character_fallback_without_losing_characters():
    text = "unbreakabletoken"
    chunks = chunk_documents(
        [LoadedDocument(name="guide", title=None, text=text)],
        chunk_size=5,
        overlap=0,
    )

    assert all(len(chunk.text) <= 5 for chunk in chunks)
    assert "".join(chunk.text for chunk in chunks) == text


def test_chunks_preserve_requested_overlap():
    document = LoadedDocument(
        name="integrations",
        title=None,
        text="First sentence. Second sentence. Third sentence.",
    )

    chunks = chunk_documents([document], chunk_size=36, overlap=20)

    assert chunks[0].text.endswith("Second sentence.")
    assert chunks[1].text.startswith("Second sentence.")
    assert all(len(chunk.text) <= 36 for chunk in chunks)


def test_chunking_preserves_all_non_whitespace_content_and_deterministic_order():
    text = (
        "# Setup Guide\n\n"
        "First unique paragraph explains authentication.\n\n"
        "- Rotate credentials on schedule.\n"
        "- Validate callback URLs before publishing.\n\n"
        "Final unique paragraph contains integration details."
    )
    document = LoadedDocument(name="setup", title="Setup Guide", text=text)

    chunks = chunk_documents([document], chunk_size=48, overlap=12)
    repeated = chunk_documents([document], chunk_size=48, overlap=12)

    reconstructed = chunks[0].text
    for chunk in chunks[1:]:
        overlap_length = max(
            (
                length
                for length in range(1, min(len(reconstructed), len(chunk.text)) + 1)
                if reconstructed.endswith(chunk.text[:length])
            ),
            default=0,
        )
        reconstructed += chunk.text[overlap_length:]

    assert "".join(reconstructed.split()) == "".join(text.split())
    assert chunks == repeated
    assert [chunk.chunk_id for chunk in chunks] == [
        f"setup-{index}" for index in range(len(chunks))
    ]
    assert all(chunk.document == "setup" for chunk in chunks)
    assert all(chunk.title == "Setup Guide" for chunk in chunks)
    assert all(len(chunk.text) <= 48 for chunk in chunks)


@pytest.mark.parametrize("chunk_size", [0, -1])
def test_invalid_chunk_size_raises_clear_error(chunk_size):
    with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
        chunk_documents([], chunk_size=chunk_size)


@pytest.mark.parametrize("overlap", [-1, 5])
def test_invalid_overlap_raises_clear_error(overlap):
    with pytest.raises(ValueError, match="overlap"):
        chunk_documents([], chunk_size=5, overlap=overlap)


@pytest.mark.parametrize("text", ["", " \n\t "])
def test_empty_or_whitespace_document_produces_no_chunks(text):
    document = LoadedDocument(name="empty", title=None, text=text)

    assert chunk_documents([document]) == []
