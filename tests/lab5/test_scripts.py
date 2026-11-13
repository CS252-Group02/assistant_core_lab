"""Exercise supplied scripts on disposable databases, never assistant.db."""

import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

from assistant_api.db import Repository, make_engine

ROOT = Path(__file__).resolve().parents[2]


def run_script(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", timeout=30,
    )


def test_migrations_are_repeatable_and_preserve_data(tmp_path):
    path = tmp_path / "migrated.db"
    script = ROOT / "scripts/migrate.py"
    first = run_script(script, path)
    assert first.returncode == 0, first.stdout + first.stderr
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0] == 2
        db.execute("INSERT INTO chat_session VALUES ('existing', 'web', '2026-01-01')")
    second = run_script(script, path)
    assert second.returncode == 0, second.stdout + second.stderr
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0] == 2
        assert db.execute("SELECT id FROM chat_session").fetchall() == [("existing",)]
        assert db.execute("SELECT COUNT(*) FROM faq").fetchone()[0] == 0
    engine = make_engine(f"sqlite:///{path.as_posix()}")
    try:
        repository = Repository(engine, "test-salt")
        repository.record_interaction("s", "r1", "fee", None, True, False, 3.0)
        assert repository.add_feedback("r1", 1, None) is not None
    finally:
        engine.dispose()


def test_seed_generates_synthetic_data(tmp_path):
    path = tmp_path / "seed.db"
    result = run_script(ROOT / "scripts/seed.py", path, 300)
    assert result.returncode == 0, result.stdout + result.stderr
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM interaction").fetchone()[0] == 300
        assert db.execute("SELECT COUNT(*) FROM feedback").fetchone()[0] > 0
        assert db.execute("SELECT COUNT(*) FROM chat_session WHERE id LIKE 'student-%'").fetchone()[0] == 0


def checker_fixture(tmp_path):
    """Use a one-question fake exercise to test the checker, not solve Q1-Q15."""
    script = tmp_path / "check.py"
    shutil.copyfile(ROOT / "practice/check.py", script)
    (tmp_path / "expected.json").write_text(
        json.dumps({"Q1": {"rows": [[42]], "ordered": True}}), encoding="utf-8"
    )
    with sqlite3.connect(tmp_path / "school.db"):
        pass
    return script, tmp_path / "my_answers.sql"


def test_checker_strict_accepts_complete_answers(tmp_path):
    script, answers = checker_fixture(tmp_path)
    answers.write_text("-- Q1\nSELECT 42;\n", encoding="utf-8")
    result = run_script(script, "--strict")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Score: 1/1" in result.stdout


def test_checker_strict_rejects_missing_and_wrong_answers(tmp_path):
    script, answers = checker_fixture(tmp_path)
    for sql in ["-- Q1\n", "-- Q1\nSELECT 7;\n", "-- Q1\nSELECT missing;\n"]:
        answers.write_text(sql, encoding="utf-8")
        result = run_script(script, "--strict")
        assert result.returncode == 1
        assert "Score: 0/1" in result.stdout


def test_checker_keeps_default_mode_compatible(tmp_path):
    script, answers = checker_fixture(tmp_path)
    answers.write_text("-- Q1\n", encoding="utf-8")
    result = run_script(script)
    assert result.returncode == 0
    assert "Score: 0/1" in result.stdout


def test_checker_strict_accepts_custom_answers_path(tmp_path):
    script, answers = checker_fixture(tmp_path)
    custom = answers.with_name("custom_answers.sql")
    custom.write_text("-- Q1\nSELECT 42;\n", encoding="utf-8")
    result = run_script(script, custom, "--strict")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Score: 1/1" in result.stdout
