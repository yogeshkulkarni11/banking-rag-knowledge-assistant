from pathlib import Path

from src.rag import load_documents


def test_load_documents_creates_chunks():
    chunks = load_documents(Path("data/documents"))
    assert len(chunks) >= 10
    assert all(chunk.text for chunk in chunks)
    assert all(chunk.source.endswith(".md") for chunk in chunks)


def test_expected_topics_are_present():
    chunks = load_documents(Path("data/documents"))
    corpus = " ".join(chunk.text.lower() for chunk in chunks)
    for topic in ["savings account", "upi", "emi", "phishing"]:
        assert topic in corpus
