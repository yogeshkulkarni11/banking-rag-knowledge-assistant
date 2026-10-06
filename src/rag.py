from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "data" / "documents"


@dataclass
class DocumentChunk:
    text: str
    source: str
    chunk_id: str


def load_documents(doc_dir: Path = DOCS_DIR) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in sorted(doc_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        sections = [s.strip() for s in text.split("\n## ") if s.strip()]
        for index, section in enumerate(sections):
            if index > 0:
                section = "## " + section
            chunks.append(
                DocumentChunk(
                    text=section,
                    source=path.name,
                    chunk_id=f"{path.stem}-{index}",
                )
            )
    return chunks


class BankingRAG:
    def __init__(self) -> None:
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.collection_name = os.getenv("CHROMA_COLLECTION", "banking_knowledge")
        self.chroma_path = os.getenv("CHROMA_PATH", str(ROOT / "chroma_db"))
        self.top_k = int(os.getenv("TOP_K", "4"))
        self.embedder = SentenceTransformer(self.embedding_model_name)
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Synthetic banking knowledge base"},
        )

    def index_documents(self, chunks: Iterable[DocumentChunk] | None = None) -> int:
        chunks = list(chunks or load_documents())
        if not chunks:
            return 0
        embeddings = self.embedder.encode(
            [c.text for c in chunks], normalize_embeddings=True
        ).tolist()
        self.collection.upsert(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[{"source": c.source} for c in chunks],
            embeddings=embeddings,
        )
        return len(chunks)

    def retrieve(self, question: str, top_k: int | None = None) -> list[dict]:
        if self.collection.count() == 0:
            self.index_documents()
        query_embedding = self.embedder.encode(
            [question], normalize_embeddings=True
        ).tolist()
        result = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k or self.top_k,
            include=["documents", "metadatas", "distances"],
        )
        rows = []
        for doc, metadata, distance in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            rows.append({"text": doc, "source": metadata["source"], "distance": distance})
        return rows

    def answer(self, question: str) -> str:
        contexts = self.retrieve(question)
        context_text = "\n\n".join(
            f"[{i + 1}] {item['text']} (source: {item['source']})"
            for i, item in enumerate(contexts)
        )
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or OpenAI is None:
            return (
                "LLM mode is not configured. Relevant retrieved context:\n\n"
                + context_text
            )

        client_kwargs = {"api_key": api_key}
        if os.getenv("OPENAI_BASE_URL"):
            client_kwargs["base_url"] = os.getenv("OPENAI_BASE_URL")
        client = OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a banking knowledge assistant. Answer only from the supplied "
                        "context. If the context does not contain the answer, say you do not "
                        "have enough information. Do not invent bank policies. Cite sources "
                        "using [1], [2], etc."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_text}\n\nQuestion: {question}",
                },
            ],
        )
        return response.choices[0].message.content or "No answer generated."
