import sqlite3
from pathlib import Path

import pytest
import school_repo as repo

SQL = (Path(__file__).parent / "school.sql").read_text(encoding="utf-8")


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")          # a fresh in-memory copy for every test
    c.executescript(SQL)
    yield c
    c.close()


def test_example_students_in_program(con):
    assert repo.students_in_program(con, "CS") == ["An", "Chi", "Hoa"]


def test_d1_add_student(con):
    new_id = repo.add_student(con, "Minh", 1, "CS")
    assert new_id == 9
    assert "Minh" in repo.students_in_program(con, "CS")


def test_d1_no_sql_injection(con):
    repo.add_student(con, "Robert'); DROP TABLE students;--", 1, "CS")
    assert con.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 9     # table still there



def test_d1_commits_and_preserves_input(tmp_path):
    path = tmp_path / "school.db"
    name = "x', 1, 'CS'); DROP TABLE students;--"
    program = "CS'); DROP TABLE courses;--"
    with sqlite3.connect(path) as writer:
        writer.executescript(SQL)
        new_id = repo.add_student(writer, name, 2, program)
        assert not writer.in_transaction
        with sqlite3.connect(path) as reader:
            assert reader.execute(
                "SELECT name, year, program FROM students WHERE id = ?", (new_id,)
            ).fetchone() == (name, 2, program)
            assert reader.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 9
            assert reader.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 5


def test_d1_stores_fields_and_returns_unique_ids(con):
    first_id = repo.add_student(con, "Minh", 1, "CS")
    second_id = repo.add_student(con, "Lan", 3, "SE")
    assert isinstance(first_id, int)
    assert isinstance(second_id, int)
    assert first_id != second_id
    assert con.execute(
        "SELECT id, name, year, program FROM students WHERE id IN (?, ?) ORDER BY id",
        (first_id, second_id),
    ).fetchall() == [(first_id, "Minh", 1, "CS"), (second_id, "Lan", 3, "SE")]


@pytest.mark.parametrize("name, program", [
    ("Nguyễn Thị Ánh", "Khoa học máy tính"),
    ("O'Connor", "Student's program"),
])
def test_d1_preserves_unicode_and_quotes(con, name, program):
    new_id = repo.add_student(con, name, 2, program)
    assert con.execute(
        "SELECT name, year, program FROM students WHERE id = ?", (new_id,)
    ).fetchone() == (name, 2, program)


def test_d2_average_grade(con):
    assert repo.average_grade(con, "CSC10004") == 5.25
    assert repo.average_grade(con, "XYZ") is None


def test_d3_transcript(con):
    assert repo.transcript(con, 2) == [("Computational Thinking", 3, None), ("Data Structures and Algorithms", 4, 5.5),
                                       ("Fundamentals of Programming", 4, 7.0)]
