from app import indexing
from app.ingestion import DocumentChunk, LoadedDocument


class FakeVectorStore:
	def __init__(self):
		self.indexed_chunks = None

	def index_chunks(self, chunks):
		self.indexed_chunks = chunks


def test_index_knowledge_base_loads_chunks_and_returns_indexed_count(tmp_path):
	(tmp_path / "authentication.md").write_text(
		"# Authentication\nOAuth redirect setup.", encoding="utf-8"
	)
	store = FakeVectorStore()

	count = indexing.index_knowledge_base(data_dir=tmp_path, vector_store=store)

	assert count == 1
	assert store.indexed_chunks == [
		DocumentChunk(
			chunk_id="authentication-0",
			document="authentication",
			title="Authentication",
			text="# Authentication\nOAuth redirect setup.",
		)
	]


def test_provided_data_directory_is_passed_to_document_loader(monkeypatch, tmp_path):
	expected_document = LoadedDocument(
		name="provided", title="Provided", text="A short document."
	)
	loader_calls = []

	def fake_load_documents(data_dir):
		loader_calls.append(data_dir)
		return [expected_document]

	monkeypatch.setattr(indexing, "load_documents", fake_load_documents)
	store = FakeVectorStore()

	count = indexing.index_knowledge_base(data_dir=tmp_path, vector_store=store)

	assert loader_calls == [tmp_path]
	assert count == 1
	assert store.indexed_chunks[0].document == "provided"


def test_provided_vector_store_is_used_without_constructing_default(monkeypatch):
	document = LoadedDocument(name="test", title=None, text="Text")
	monkeypatch.setattr(indexing, "load_documents", lambda: [document])
	store = FakeVectorStore()

	def unexpected_vector_store():
		raise AssertionError("A VectorStore should not be constructed when provided.")

	monkeypatch.setattr(indexing, "VectorStore", unexpected_vector_store)

	count = indexing.index_knowledge_base(vector_store=store)

	assert count == 1
	assert len(store.indexed_chunks) == 1


def test_blank_documents_index_empty_chunk_list_and_return_zero(tmp_path):
	(tmp_path / "blank.md").write_text(" \n\t ", encoding="utf-8")
	store = FakeVectorStore()

	count = indexing.index_knowledge_base(data_dir=tmp_path, vector_store=store)

	assert count == 0
	assert store.indexed_chunks == []