# TV7 verification report

## Source and environment

- Verification date: November 13, 2026.
- Team repository: https://github.com/CS252-Group02/assistant_core_lab
- Base commit: `89fd1a0a3b710a57ca303a32744c7dede0437732`.
- Work branch: `feat/lab05-tv7-checker-design-evidence`.
- Reference: instructor `public_materials/lab05` and the team acceptance contract
  in `docs/lab5/README.md`.
- Runtime: isolated Python 3.11.9 on Windows; pinned `requirements.txt` installed.
  The local embedded runtime points to this checkout's `src`; runtime files,
  scratch logs and test databases are ignored and are not submission content.
- Dependencies: `python -m pip check` reports no broken requirements.
- FastAPI regression tests were run outside the restricted agent sandbox, whose
  Windows socketpair restriction blocks TestClient startup. No real weather or
  LLM service was used.

## Measured checks

| Check | Measured result | Exit code |
| --- | --- | --- |
| Four supplied checker tests plus eight additional CLI cases | 12 passed, 2 unrelated script tests deselected | 0 |
| Existing Lab 4/core regression tests | 55 passed | 0 |
| Ruff across src, tests, practice and scripts | All checks passed | 0 |
| Ruff format check of the two changed Python files | 2 files already formatted | 0 |
| `git diff --check` | No whitespace errors | 0 |
| Ordinary checker on the team's blank answers | Score: 0/15 | 0 |
| Strict checker on the same blank answers | Score: 0/15 | 1 |
| Full practice and acceptance suite | 77 passed, 42 failed; no skips or collection errors | 1 |

Starlette emits one upstream AnyIO deprecation warning; it does not fail tests.
The 42 full-suite failures are outside the TV7 checker: 15 school answers, four
analytics queries, four Python-practice cases, five repository cases, ten API
persistence cases, two configuration cases, and two migration/seed integration
cases. These identify incomplete TV1-TV6 work at this base commit, not a claim
that final integration is complete. Existing acceptance tests are unchanged.

## Reproduce

With the repository's normal Python 3.11 environment active, run from the root:

```powershell
python -m pip check
python -m pytest -q tests/lab5/test_scripts.py tests/lab5/test_checker_cli.py -k checker
python -m pytest -q tests --ignore=tests/lab5
python -m ruff check src tests practice scripts --no-cache
python -m ruff format --check practice/check.py tests/lab5/test_checker_cli.py
python practice/make_school_db.py
python practice/check.py
$LASTEXITCODE
python practice/check.py --strict
$LASTEXITCODE
```

For restricted Windows temp directories, create `.lab5-tmp` and pass a fresh
`--basetemp=.lab5-tmp/<run-name>` plus `-p no:cacheprovider` to pytest.
Do not rerun the database builder against valuable or manually edited data.

## Checker behavior covered

- Complete, correct answers return 0 in strict mode.
- Missing answers, wrong results and SQL errors print a score and return 1.
- Default mode keeps returning 0 after scoring incomplete or erroneous answers.
- Custom answers paths work with and without strict mode, with the flag before
  or after the path; paths containing spaces are tested.
- Ordered questions reject reversed rows; unordered questions accept equivalent
  row sets in a different order.
- Help works without a database; unknown CLI options exit 2.
- Missing database/answers files return 1 with a readable error.
- No answers or expected results are hardcoded in the checker.

Tests use independent one-question exercises. Passing these checks does not mean
that the team's currently blank Q1-Q15 submission has achieved 15/15.

## Submission readiness

The checker, completed worksheet, ER diagram and demo runbook are ready for TV1
review. The final 15/15 score, successful persistence/restart screenshots and
analytics output must be captured after the relevant integrations are complete.
Follow [the submission/demo guide](submission-evidence.md). Do not mark those
pending items complete merely because the TV7 checker tests pass.
