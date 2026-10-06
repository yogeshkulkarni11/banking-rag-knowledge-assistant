from pathlib import Path

from src.rag import load_documents


def test_each_source_produces_multiple_semantic_chunks():
    chunks = load_documents(Path("data/documents"))
    sources = {chunk.source for chunk in chunks}
    assert len(sources) == 5
    for source in sources:
        assert sum(chunk.source == source for chunk in chunks) >= 2
