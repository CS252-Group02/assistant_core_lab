# Lab 5 submission and demo evidence

## Scope and ownership

TV7 owns the strict SQL checker, bonus design review, ER diagram and submission
verification. TV1 reviews this work. TV1-TV6 own the exercise answers, analytics,
repository, API integration, configuration, migrations and seed data. Do not
replace their implementation or change the supplied acceptance tests for a demo.
All saved examples must be synthetic. Keep `.env`, salts and database files out
of Git and screenshots.

## Deliverables

- `practice/check.py`: compatible score-only CLI and optional strict exit codes.
- `tests/lab5/test_checker_cli.py`: isolated CLI regression tests, in addition to
  the four supplied checker acceptance tests in `test_scripts.py`.
- `docs/lab5/data_model.md`: all worksheet tables completed in English.
- `docs/lab5/data-model.md`: Mermaid ER diagram, keys/cardinalities and design gaps.
- `docs/lab5/tv7-verification.md`: measured local verification results and scope.
- `docs/lab5/results.md`: TV3 supplies actual F1-F3/H2 results after integration.

## Reproduce TV7 checks

From the repo root with Python 3.11 and the pinned requirements installed:

```powershell
python -m pytest -q tests/lab5/test_scripts.py -k checker
python -m pytest -q tests/lab5/test_checker_cli.py
python -m ruff check practice/check.py tests/lab5/test_checker_cli.py
python practice/make_school_db.py
python practice/check.py
python practice/check.py --strict
$LASTEXITCODE
```

The default checker must print its score and exit 0 even while answers are
unfinished. Strict mode must print the same score and exit 1 until every answer
is correct. Exit 1 in this case is expected proof that strict mode works, not a
checker defect. Once TV1-TV2 finish Q1-Q15, strict mode must print `Score: 15/15`
and exit 0. Invalid CLI syntax exits 2. Setup errors, such as missing files,
exit 1 and report a readable message.

## Final integrated demo procedure

The following is a handoff runbook, not a claim that the pending integrations
already pass. Record actual results after merging TV1-TV6, then update the
verification report with the final commit and environment.

1. Run `python scripts/check_lab5.py` and capture the summary and exit code.
   Also capture `python practice/check.py --strict` showing 15/15 and exit 0.
2. Use a disposable database and a private stable local salt in `.env`; never
   display its value. Apply migrations twice. The second run must skip applied
   files and preserve data. Run seed with 300 synthetic interactions on a fresh
   disposable database. Verify the count, not just the seed script's printout.
3. Launch `python -m uvicorn assistant_api.main:create_app --factory --reload`.
   Open `/docs`, send a synthetic chat message such as `hello`, and copy the
   returned `request_id` without capturing the admin key or raw session ID.
4. Submit feedback for that request. Capture HTTP 201, the generated ID and UTC
   timestamp. Send feedback with a nonexistent request ID; capture HTTP 404 and
   `unknown_request_id`. A rating of 5 must produce HTTP 422.
5. Verify GET feedback and GET intent stats return 401 without/with a wrong key;
   supply the local admin key privately and capture only successful responses.
6. Stop the server, restart with the same database URL and salt, then list
   feedback. The previously saved feedback must remain. Show that interactions
   contain metadata and session hashes, not raw message/name/phone columns.
7. Run F1-F3/H2; TV3 records real output and explanations in `results.md`.
8. Capture successful offline acceptance tests and the ER diagram preview.
   Request TV1 review. The Tech Lead merges approved work and tags `v0.5-data`
   after final checks. Submit the PR/tag links according to the instructor's
   deadline and the agreed late-submission policy.

## Evidence checklist

| Evidence | Required observation | Current status |
| --- | --- | --- |
| Strict checker regression tests | Correct exit codes, ordinary/custom-path compatibility | See measured TV7 report |
| Worksheet and ER diagram | Six critiques, storage decisions, keys and relationships | Written; TV1 review pending |
| Submitted school answers | 15/15 and strict exit 0 | Pending TV1-TV2; blank starter is not a pass |
| D1-D3 | Practice tests pass, including injection test | Pending TV1-TV3 |
| R1-R2 and API persistence | Known/unknown requests, ordering, limit, restart survival | Pending TV4-TV5 |
| DB configuration, migrations and 300-row seed | Environment loading, repeatability and compatible schema | Pending TV6 and R1 integration |
| F1-F3/H2 | Query output and interpretation on synthetic data | Pending TV3 |
| Final integrated demo | Actual screenshots/logs from the merged implementation | Pending integration; not fabricated |
| Review, PR and tag links | TV1 approval and Tech Lead tag | Add real links when available |

## Suggested PR content

Title: `feat(lab5): add strict SQL checks and TV7 design evidence`

Describe the strict/default exit-code contract, link both design documents, and
report the measured scoped results from `tv7-verification.md`. State separately
that final integrated evidence is pending if teammates' tasks are still open.
Link the actual task issue; do not invent an issue number.

AI use: OpenAI Codex helped implement the checker, add isolated CLI tests, review
the supplied schema and prepare English documentation. Verification results are
measured; the student must review and understand the retained code and design.
