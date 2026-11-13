"""Execute submitted SQL against known, isolated datasets."""

import json
import re
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = json.loads((ROOT / "practice/expected.json").read_text(encoding="utf-8"))


def read_queries(path):
    parts = re.split(r"^--\s*(Q\d+)\b.*$", path.read_text(encoding="utf-8"), flags=re.M)
    return {
        parts[i]: "\n".join(
            line for line in parts[i + 1].splitlines() if not line.strip().startswith("--")
        ).strip()
        for i in range(1, len(parts), 2)
    }


@pytest.fixture
def school():
    with sqlite3.connect(":memory:") as db:
        db.executescript((ROOT / "practice/school.sql").read_text(encoding="utf-8"))
        yield db


@pytest.mark.parametrize("question", [f"Q{i}" for i in range(1, 16)])
def test_school_answers(school, question):
    query = read_queries(ROOT / "practice/my_answers.sql").get(question, "")
    assert query, f"Implement {question} in practice/my_answers.sql"
    actual = [list(row) for row in school.execute(query).fetchall()]
    expected = EXPECTED[question]
    if expected["ordered"]:
        assert actual == expected["rows"]
    else:
        assert sorted(map(repr, actual)) == sorted(map(repr, expected["rows"]))


@pytest.fixture
def analytics_db():
    with sqlite3.connect(":memory:") as db:
        db.executescript((ROOT / "sql/migrations/001_init.sql").read_text(encoding="utf-8"))
        db.execute("INSERT INTO chat_session VALUES ('hash', 'web', '2026-01-01 08:00:00')")
        db.executemany(
            "INSERT INTO interaction "
            "(request_id, session_id, intent, topic, latency_ms, created_at) VALUES (?, 'hash', ?, ?, ?, ?)",
            [
                ("r1", "rule", "H26-5.3", 10, "2026-01-01 08:00:00"),
                ("r2", "rule", "H26-5.3", 20, "2026-01-01 08:10:00"),
                ("r3", "fee", None, 5, "2026-01-01 09:00:00"),
                ("r4", "rule", "H26-4.2", 30, "2026-01-01 10:00:00"),
            ],
        )
        db.executemany(
            "INSERT INTO feedback (request_id, rating, created_at) VALUES (?, ?, '2026-01-01 10:01:00')",
            [("r1", -1), ("r2", -1), ("r3", 1), ("r4", -1)],
        )
        yield db


@pytest.mark.parametrize("question, expected", [
    ("Q1", [("rule", 3), ("fee", 1)]),
    ("Q2", [("rule", 20.0), ("fee", 5.0)]),
    ("Q3", [("H26-5.3", 2), ("H26-4.2", 1)]),
    ("Q4", [("08", 2), ("09", 1), ("10", 1)]),
])
def test_assistant_queries(analytics_db, question, expected):
    query = read_queries(ROOT / "sql/my_queries.sql").get(question, "")
    assert query, f"Implement {question} in sql/my_queries.sql (see the query contract in docs/lab5/README.md)"
    assert analytics_db.execute(query).fetchall() == expected
