import pytest

from app.ingestion import load_documents


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