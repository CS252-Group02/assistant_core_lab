"""Run a small, reproducible BM25 exploration over the handbook rules."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDBOOK_PATH = ROOT / "data" / "handbook.json"
TOKEN_RE = re.compile(r"[a-z0-9]+")


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
