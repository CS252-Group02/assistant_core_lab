# Lab 5 technical setup notes

## Source materials

Complete SQL Q1-Q15 (15/15), Python D1-D3, repository R1-R2, persistent feedback,
F1-F3, H2, and the bonus design worksheet. The source is the instructor's
`public_materials/lab05` and the 24-page Lab 5 PDF. The public-materials repository
is a reference; edit this repository only. Runtime and tests must not depend
on the sibling reference folder.

## What is supplied and what is unfinished

- `practice/` is copied from the instructor: school schema, expected answers,
  checker, database builder, unfinished D1-D3, and five tests. Q1-Q15 stay blank.
- `src/assistant_api/db.py` contains the supplied models, hashing, engine helper,
  `record_interaction`, and intent aggregation. R1 and R2 remain unfinished.
- The numbered migrations and migrate/seed scripts are supplied examples, not
  missing exercises. Their behavior and compatibility are covered by tests.
- The current API retains Lab 4 behavior. `create_app(..., repo=None)` reserves
  the injection interface but does not use it yet.
- The DB environment variables are in `.env.example`; their settings are unfinished. Baseline duplicate settings and import issues have been cleaned up.
- `tests/lab5/` supplies offline acceptance tests. Do not weaken tests to make
  unfinished work appear complete.
- `sql/my_queries.sql` and the design worksheet are unfinished. Keep the query
  markers intact. The actual exercise file is `sql/my_queries.sql`, not the
  `sql/queries.sql` path mentioned in the starter README.

## Acceptance test interfaces

- Keep `AssistantService.handle()` and existing API routes, including `/v1/offices`.
- `create_app(settings=None, service=None, weather=None, repo=None)` must use an
  injected repository. Without one, build it using the configured DB URL and salt.
- Add `Settings.database_url` (default `sqlite:///assistant.db`) and
  `Settings.session_salt` (excluded from repr), reading `DATABASE_URL` and
  `SESSION_SALT` in `load_settings`. Use a stable private salt for local persistent
  data. Tests inject fixed fake salts. Never commit a real secret.
- Implement `add_feedback(request_id, rating, comment) -> Feedback | None`
  and `list_feedback(limit=100) -> list[Feedback]` using the supplied signatures.
  The list is newest first; limit zero returns an empty list. The default is 100.
- Chat records the same request ID returned to the caller, salted session hash,
  intent, first source ID as topic (or null), latency, timestamp, resolved, and degraded.
  Follow the starter rule: `resolved = intent != 'unknown'`; degraded is independent.
- Do not save raw messages, raw session IDs, names, or phone numbers in the DB.
  Optional feedback comments are allowed; use synthetic comments in evidence.
- Feedback returns 201 for a known request, 404 for an unknown request, and 422
  for invalid input. Keep the current error envelope; unknown request code is
  `unknown_request_id`. Feedback ratings remain -1, 0, or 1.
- `GET /v1/feedback?limit=100` and `GET /v1/stats/intents` require the admin key.
  Stats returns objects with `intent`, `requests`, `avg_latency_ms`, and `unresolved`.
  The last field is a count, not a fraction. Round mean latency to one decimal.
- Tests must use mocked weather, stub LLMs, and isolated databases. A real
  network service must never be needed to pass a test.

## SQL analytics contract

Write one SELECT under each marker in `sql/my_queries.sql`. These column orders
and sorting rules let acceptance tests compare known results without relying on
random seed output. Aliases below are recommended for readable reports.

| Marker | Question | Output columns and order |
| --- | --- | --- |
| Q1 / F1 | Requests per intent | `intent, requests`; requests descending, then intent ascending |
| Q2 / F2 | Mean latency per intent | `intent, avg_latency_ms`; rounded to 1 decimal; same ordering as Q1 |
| Q3 / F3 | Topics receiving thumbs-down | `topic, thumbs_down`; join on request_id, rating -1; count descending, then topic ascending; retain the null group if present |
| Q4 / H2 | Busiest UTC hours | `hour, requests`; hour is a two-character string `00`-`23`; count descending, then hour ascending |

Record the seed results and a short explanation in `docs/lab5/results.md`.
For F3, each thumbs-down feedback row contributes one count, including repeated
feedback for a request. H2 is fixed to requests by UTC hour so no further product
decision is required before implementation.

## Focused tests

Activate the Python 3.11 environment and run commands from the repository root.
For individual pytest commands, add a fresh `--basetemp` path if your sandbox
blocks the system temp directory. The all-in-one runner handles this automatically.

| Component | Focused check |
| --- | --- |
| SQL practice | `python -m pytest -q tests/lab5/test_sql.py -k school_answers` |
| Python practice | `python -m pytest -q practice/test_school_repo.py` |
| Analytics | `python -m pytest -q tests/lab5/test_sql.py -k assistant_queries` |
| Repository | `python -m pytest -q tests/lab5/test_db.py tests/lab5/test_repository.py` |
| API | `python -m pytest -q tests/lab5/test_api_persistence.py` |
| Configuration/scripts | `python -m pytest -q tests/lab5/test_config.py tests/lab5/test_scripts.py -k "not checker"` |
| SQL checker | `python -m pytest -q tests/lab5/test_scripts.py -k checker` |

The checker supports optional `--strict` without breaking its existing default
or optional answers-path argument. Strict mode prints the usual score and exits
0 only for full marks, otherwise 1 (missing answers, incorrect results, SQL errors).
The argparse CLI accepts the flag before or after a custom answers path.
Input/setup errors exit 1; argument usage errors exit 2. No SQL
answers should be hardcoded into the checker.

Some seed/migration tests also depend on R1. This is an implementation dependency. The supplied scripts already create their schema;
Ensure migrations and ORM-created databases both work with the repository.
