# TV4 implementation report

## Scope and source

Completed repository tasks R1–R2 on top of the instructor-derived database module
already integrated into main (base commit `51bb6f1`).
The API integration remains TV5's work; database configuration, migrations, and
seed scripts remain TV6's work.

## Changes completed

- Reviewed the supplied models, salted hashing, interaction recording, and intent statistics.
- R1: `add_feedback()` checks the request exists, creates feedback, commits,
  refreshes its generated fields, and returns it. Unknown requests return `None`.
- R2: `list_feedback()` returns feedback ordered by descending creation time,
  limited to the requested number (default 100).
- Retained dependency declarations already merged by teammates; this PR does not change dependencies.
- Added `tests/lab5/test_tv4_repository.py` with three starter-derived checks and six additional verification tests.
- Used postponed annotations and explicit ORM relationship targets to address
  failures observed with SQLModel 0.0.22 on the available Python 3.15 runtime.
  Table names, columns, and repository signatures remain compatible with the starter.

## Verification results

- Initial verification on the older branch: 55 baseline tests, then 64 passed.
- Final verification on updated main: **20 database tests passed** across the three
  database/repository test modules.
- Full suite: **121 passed, 12 failed**. Ten failures are in API persistence tests;
  two are in database settings tests. Current API code still uses in-memory storage,
  and Settings lacks database_url/session_salt. These are TV5/TV6 handoff items.
- Ruff checks on the changed Python files: passed.
- The full suite emits 352 dependency deprecation warnings on Python 3.15.

Database tests verify:

1. Persisted session IDs match the salted hash rather than the raw ID.
2. Multiple interactions reuse a session row.
3. Feedback requires an existing interaction and receives a database ID.
4. Feedback survives engine disposal and reopening a file-backed database.
5. Feedback ordering uses explicit timestamps, with empty and zero-limit cases.
6. Unknown feedback requests do not insert rows.
7. Hashing is deterministic, salt-sensitive, and retains the starter's 16-character
   format; interaction models have no message or raw-session field.
8. Intent statistics handle empty data and return correct counts, average latency,
   and unresolved counts.
9. A duplicate request ID rolls back creation of a new session in that transaction.

Tests ran using a temporary environment at `/tmp/tv4-lab05-venv`, with SQLModel
0.0.22 and SQLAlchemy 2.0.57 plus existing system packages. This is not a clean
installation of every pinned requirement: the machine's Python 3.15 environment
has newer existing packages. Repeat the team's normal install/test workflow on
its supported Python environment before merging.

```sh
PYTHONPATH="$PWD/src" /tmp/tv4-lab05-venv/bin/python -m pytest -q
/tmp/tv4-lab05-venv/bin/python -m pytest -q tests/lab5/test_db.py tests/lab5/test_repository.py tests/lab5/test_tv4_repository.py
python3 -m ruff check src/assistant_api/db.py tests/lab5/test_tv4_repository.py
```

## Model/repository review and TV6 handoff

- Relationships match the supplied migration: session → interactions via
  `session_id`, interaction → feedback via unique `request_id`.
- The SQL migration includes a feedback rating CHECK constraint; the supplied ORM
  model relies on API validation. Agree on matching enforcement for both schema
  creation paths before final integration.
- Foreign keys are declared, but the starter engine does not enable SQLite's
  `PRAGMA foreign_keys=ON`. R1 explicitly checks interaction existence, but this
  does not replace database-level enforcement for other writers.
- The stored session ID is SHA-256 truncated to 16 hexadecimal characters, exactly
  as in the starter. Keep the salt stable across restarts and load it from configuration.
- No raw question or raw session identifier is saved by this repository. Optional
  feedback comments remain stored as supplied, as required by the lab.

These are integration findings, not claims that migrations have been tested here.

## TV5 API review and handoff

The current `src/assistant_api/main.py` still uses an in-memory feedback list,
does not record interactions, and has no intent-statistics endpoint. Therefore
API-level persistence and restart behavior cannot yet be signed off.

Use the supplied starter API integration to:

- Accept an injectable Repository in `create_app()` and initialize it from TV6's settings.
- Record chat metadata with the same request ID returned to the caller.
- Translate `add_feedback()` returning `None` into HTTP 404 and successful saves into 201.
- Serialize ORM feedback using `FeedbackOut.model_validate(..., from_attributes=True)`.
- Protect feedback listing and `/v1/stats/intents` with the existing admin-key check.
- Validate the public feedback limit so negative values cannot bypass the intended limit.
- Preserve the current `/v1/offices` route, which is absent from the starter API file.
- Verify chat → feedback → restart → authenticated retrieval, plus existing API tests.

The repository persistence test passes; an API restart demonstration remains pending
TV5's integration. TV5 is also the assigned reviewer of this TV4 implementation.
