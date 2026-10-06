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
    document = LoadedDocument(name="payments", title="Payment Guide", text="abcdefghijkl")

    chunks = chunk_documents([document], chunk_size=5, overlap=2)

    assert [chunk.text for chunk in chunks] == ["abcde", "defgh", "ghijk", "jkl"]
    assert [chunk.chunk_id for chunk in chunks] == [
        "payments-0",
        "payments-1",
        "payments-2",
        "payments-3",
    ]
    assert all(chunk.document == "payments" for chunk in chunks)
    assert all(chunk.title == "Payment Guide" for chunk in chunks)
    assert chunk_documents([document], chunk_size=5, overlap=2) == chunks


def test_chunks_preserve_requested_overlap():
    document = LoadedDocument(name="integrations", title=None, text="abcdefgh")

    chunks = chunk_documents([document], chunk_size=5, overlap=2)

    assert chunks[0].text[-2:] == chunks[1].text[:2]


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
