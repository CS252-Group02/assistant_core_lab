"""Run a small, reproducible BM25 exploration over the handbook rules."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDBOOK_PATH = ROOT / "data" / "handbook.json"
TOKEN_RE = re.compile(r"[a-z0-9]+")
K1 = 1.5
B = 0.75


@dataclass(frozen=True)
class Chunk:
    id: str
    title: str
    text: str

    @property
    def content(self) -> str:
        return f"{self.title} {self.text}"


def tokenize(text: str) -> list[str]:
    """Lowercase and split text into alphanumeric tokens."""
    return TOKEN_RE.findall(text.lower())


def load_chunks() -> list[Chunk]:
    """Load each handbook rule as one retrieval chunk."""
    data = json.loads(HANDBOOK_PATH.read_text(encoding="utf-8"))
    return [Chunk(id=row["id"], title=row["title"], text=row["text"]) for row in data]


def bm25_scores(chunks: list[Chunk], query: str) -> list[tuple[Chunk, float]]:
    """Score each rule using BM25, including title tokens."""
    documents = [tokenize(chunk.content) for chunk in chunks]
    document_lengths = [len(document) for document in documents]
    average_length = sum(document_lengths) / len(document_lengths)
    document_frequency: dict[str, int] = {}
    for document in documents:
        for term in set(document):
            document_frequency[term] = document_frequency.get(term, 0) + 1

    query_terms = tokenize(query)
    results: list[tuple[Chunk, float]] = []
    for chunk, document, length in zip(chunks, documents, document_lengths, strict=True):
        frequencies = {term: document.count(term) for term in set(query_terms)}
        score = 0.0
        for term in query_terms:
            frequency = frequencies.get(term, 0)
            if not frequency:
                continue
            df = document_frequency[term]
            inverse_document_frequency = math.log(1 + (len(chunks) - df + 0.5) / (df + 0.5))
            normalization = frequency + K1 * (1 - B + B * length / average_length)
            score += inverse_document_frequency * frequency * (K1 + 1) / normalization
        results.append((chunk, score))
    return sorted(results, key=lambda row: (-row[1], row[0].id))
