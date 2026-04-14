from backend.ingestion.chunker import TextChunker
from backend.ingestion.loader import Document


def test_chunk_short_text():
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)
    doc = Document(content="This is a short text.")
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].content == "This is a short text."


def test_chunk_long_text():
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    text = "Word " * 100  # ~500 chars
    doc = Document(content=text, metadata={"source": "test.txt"})
    chunks = chunker.chunk_document(doc)
    assert len(chunks) > 1
    # All chunks should have metadata
    for chunk in chunks:
        assert chunk.metadata["source"] == "test.txt"
        assert "chunk_index" in chunk.metadata


def test_chunk_preserves_metadata():
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)
    doc = Document(
        content="SAP S/4HANA migration guide.",
        metadata={"source": "s4hana.pdf", "sap_module": "S4HANA"},
    )
    chunks = chunker.chunk_document(doc)
    assert chunks[0].metadata["sap_module"] == "S4HANA"


def test_chunk_empty_document():
    chunker = TextChunker()
    doc = Document(content="   ")
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 0
