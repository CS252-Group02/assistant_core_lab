"""Exercise supplied scripts on disposable databases, never assistant.db."""

import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

from sqlalchemy import inspect
from sqlmodel import Session, select

from assistant_api.db import ChatSession, Feedback, Interaction, Repository, make_engine

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
    assert first.stdout.splitlines() == ["apply 001_init.sql", "apply 002_add_faq.sql"]
    with sqlite3.connect(path) as db:
        versions = db.execute("SELECT name, applied_at FROM schema_version ORDER BY name").fetchall()
        assert [name for name, _ in versions] == ["001_init.sql", "002_add_faq.sql"]
        assert all(timestamp for _, timestamp in versions)
        schema = db.execute("SELECT name, sql FROM sqlite_master ORDER BY name").fetchall()
        db.execute("INSERT INTO chat_session VALUES ('existing', 'web', '2026-01-01')")

    engine = make_engine(f"sqlite:///{path.as_posix()}")
    try:
        repository = Repository(engine, "test-salt")
        repository.record_interaction("s", "r1", "fee", None, True, False, 3.0)
        feedback = repository.add_feedback("r1", 1, "Synthetic compatibility check")
        assert feedback is not None and feedback.id is not None
    finally:
        engine.dispose()

    second = run_script(script, path)
    assert second.returncode == 0, second.stdout + second.stderr
    assert second.stdout.splitlines() == ["skip  001_init.sql", "skip  002_add_faq.sql"]
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT name, applied_at FROM schema_version ORDER BY name").fetchall() == versions
        assert db.execute("SELECT name, sql FROM sqlite_master ORDER BY name").fetchall() == schema
        assert db.execute("SELECT channel FROM chat_session WHERE id = 'existing'").fetchone() == ("web",)
        assert db.execute("SELECT COUNT(*) FROM faq").fetchone()[0] == 0
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    engine = make_engine(f"sqlite:///{path.as_posix()}")
    try:
        with Session(engine) as db:
            saved = db.exec(select(Interaction)).one()
            assert saved.request_id == "r1" and saved.latency_ms == 3.0
            assert saved.session.id == saved.session_id
            assert len(saved.feedback) == 1
            assert saved.feedback[0].id == feedback.id
            assert saved.feedback[0].comment == "Synthetic compatibility check"
    finally:
        engine.dispose()


def test_migrated_schema_matches_repository_models(tmp_path):
    path = tmp_path / "schema.db"
    result = run_script(ROOT / "scripts/migrate.py", path)
    assert result.returncode == 0, result.stdout + result.stderr
    engine = make_engine(f"sqlite:///{path.as_posix()}")
    try:
        schema = inspect(engine)
        assert set(schema.get_table_names()) == {"schema_version", "chat_session", "interaction", "feedback", "faq"}
        for model in (ChatSession, Interaction, Feedback):
            table = model.__table__
            assert {column["name"] for column in schema.get_columns(table.name)} == set(table.columns.keys())
            assert schema.get_pk_constraint(table.name)["constrained_columns"] == ["id"]
            actual_fks = {
                (tuple(fk["constrained_columns"]), fk["referred_table"], tuple(fk["referred_columns"]))
                for fk in schema.get_foreign_keys(table.name)
            }
            expected_fks = {
                ((fk.parent.name,), fk.column.table.name, (fk.column.name,)) for fk in table.foreign_keys
            }
            assert actual_fks == expected_fks
        # SQLite's autoindex is authoritative even when SQLAlchemy's SQL parser
        # cannot reflect an inline UNIQUE declaration with starter comments.
        with sqlite3.connect(path) as db:
            unique_indexes = db.execute('SELECT name FROM pragma_index_list(\'interaction\') WHERE "unique" = 1')
            unique_columns = [
                [row[0] for row in db.execute("SELECT name FROM pragma_index_info(?)", (name,))]
                for (name,) in unique_indexes
            ]
        assert ["request_id"] in unique_columns
        assert {index["name"] for index in schema.get_indexes("interaction")} >= {
            "ix_interaction_intent", "ix_interaction_session_id", "ix_interaction_created_at",
        }
        assert "ix_feedback_request_id" in {index["name"] for index in schema.get_indexes("feedback")}
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
