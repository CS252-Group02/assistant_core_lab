# TV1: SQL practice and student insertion

TV1 implements SQL Q1–Q10 and D1 `add_student`. TV2 is the assigned reviewer.
The requirements come from the Lab 5 tutorial and the team assignment table.

## Implementation

- Q1–Q4 select columns and filter students by program or year.
- Q5–Q6 sort names descending and four-credit courses by title.
- Q7–Q9 count students, group by program, and round the course average.
- Q10 selects ungraded enrollments using `IS NULL`, ordered by student ID.
- `add_student` binds name, year, and program with `?` placeholders, commits
  the insertion, and returns the generated row ID. Input remains data,
  including SQL injection strings, apostrophes, and Vietnamese text.

## Verification

Run from the repository root:

```bash
python -m pytest -q practice/test_school_repo.py -k 'd1 or example'
python practice/make_school_db.py
python practice/check.py
git diff --check
```

Verified results: **8 passed, 2 deselected** for the focused Python tests;
**Q1–Q10 all OK**, giving **10/15** in the supplied SQL checker. Q11–Q15
belong to TV2; D2 and D3 belong to other members and are excluded here.
The database builder recreates the local, ignored `practice/school.db`.

Tests cover saved field values, distinct integer IDs for multiple inserts,
SQL injection protection, exact Unicode and quoted input, visibility from
another connection, and persistence after closing and reopening the database.
The broader Lab 5 suite previously could not load because the environment
lacked `sqlmodel`; the focused checks above do not require it.

## Review for TV2

Confirm Q1–Q10 against the tutorial and supplied expected results. Check that
D1 uses placeholders for every value, commits before returning, and returns
the inserted row ID. Run the commands above and inspect the persistence and
injection tests before approving.
