"""Additional CLI checks using disposable exercises, never submitted answers."""

import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def exercise(tmp_path):
    shutil.copyfile(ROOT / "practice/check.py", tmp_path / "check.py")
    (tmp_path / "expected.json").write_text(
        json.dumps({"Q1": {"rows": [[1], [2]], "ordered": False}}), encoding="utf-8"
    )
    connection = sqlite3.connect(tmp_path / "school.db")
    connection.close()
    return tmp_path


def run(exercise, *arguments):
    return subprocess.run(
        [sys.executable, str(exercise / "check.py"), *map(str, arguments)],
        cwd=exercise,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )


@pytest.mark.parametrize("flag_first", [False, True])
def test_custom_path_supports_both_flag_positions(exercise, flag_first):
    answers = exercise / "custom answers.sql"
    answers.write_text("-- Q1\nSELECT 2 UNION ALL SELECT 1;\n", encoding="utf-8")
    arguments = ["--strict", answers] if flag_first else [answers, "--strict"]
    result = run(exercise, *arguments)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Score: 1/1" in result.stdout


def test_strict_preserves_ordered_result_checks(exercise):
    (exercise / "expected.json").write_text(json.dumps({"Q1": {"rows": [[1], [2]], "ordered": True}}), encoding="utf-8")
    (exercise / "my_answers.sql").write_text("-- Q1\nSELECT 2 UNION ALL SELECT 1;\n", encoding="utf-8")
    result = run(exercise, "--strict")
    assert result.returncode == 1 and "Score: 0/1" in result.stdout


def test_default_mode_keeps_custom_path_and_sql_error_compatibility(exercise):
    answers = exercise / "custom.sql"
    answers.write_text("-- Q1\nSELECT missing;\n", encoding="utf-8")
    result = run(exercise, answers)
    assert result.returncode == 0
    assert "ERR" in result.stdout and "Score: 0/1" in result.stdout


def test_help_does_not_require_database(exercise):
    (exercise / "school.db").unlink()
    result = run(exercise, "--help")
    assert result.returncode == 0 and "--strict" in result.stdout


def test_unknown_option_is_usage_error(exercise):
    assert run(exercise, "--unknown-option").returncode == 2


def test_missing_database_is_setup_error(exercise):
    (exercise / "school.db").unlink()
    result = run(exercise, "--strict")
    assert result.returncode == 1 and "school.db not found" in result.stderr
    assert not (exercise / "school.db").exists()


def test_missing_answers_is_input_error(exercise):
    result = run(exercise, "absent.sql", "--strict")
    assert result.returncode == 1 and "Cannot read checker input" in result.stderr
