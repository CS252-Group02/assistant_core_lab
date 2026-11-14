# TV6 database configuration and verification

## Scope and environment

- Issue: https://github.com/CS252-Group02/assistant_core_lab/issues/24
- Branch: `feat/tv6`; base: `5056e0e` on `main`.
- Verified November 14, 2026, on Windows with isolated Python 3.11.18,
  pinned `requirements.txt`, and an editable package installation.
- Runtime/test changes verified at `b5c8740`; the following commit records this evidence.
- No server, real weather service or LLM is used by these checks. API tests run
  outside the agent sandbox's Windows socket restrictions, with mocked weather.

This work adds the database settings and completes R1 because the supplied seed
script calls it. R2, API repository integration, SQL practice and analytics are
separate team tasks. No acceptance tests are skipped or weakened.

## Environment configuration

`Settings.database_url` defaults to `sqlite:///assistant.db`. `load_settings()`
reads `DATABASE_URL` and `SESSION_SALT`, loading an optional `.env` first while
preserving variables already set in the process environment. Passing
`env_file=None` disables dotenv loading.

`Settings.session_salt` is excluded from repr. Its default `dev-only-change-me`
and the example file's salt are public placeholders, not private salts. Generate
a local value with `python -c "import secrets; print(secrets.token_hex(32))"`,
save it only in your ignored `.env` or local environment, and keep it stable for
the database's lifetime. Changing the salt changes the session hashes. Never
paste a real salt into an issue, PR, screenshot or tracked document.

Example local configuration (replace the salt placeholder privately):

```dotenv
DATABASE_URL=sqlite:///assistant.db
SESSION_SALT=replace-with-a-random-local-secret
```

Loading settings does not yet wire the repository into the API; that remains
the API integration task. Existing `Settings()` callers still work.

## Migrations and synthetic seed

From the repository root, with the Python 3.11 environment active, choose an
unused database path under the ignored scratch directory:

```powershell
New-Item -ItemType Directory -Force .lab5-tmp | Out-Null
$dbPath = ".lab5-tmp/tv6-demo-$([guid]::NewGuid().ToString('N')).db"
python scripts/migrate.py $dbPath
python scripts/migrate.py $dbPath
python scripts/seed.py $dbPath 300
```

The first migration run prints `apply 001_init.sql` and `apply 002_add_faq.sql`;
the second prints `skip` for both files. The script tracks filenames and
timestamps in `schema_version`. Tests confirm those records, the schema, a
preexisting session, an interaction and its feedback survive the second run.

These scripts accept a **SQLite file path**, not a database URL, and retain the
instructor's CLI. The seed uses `seed-salt` only for invented `student-1` through
`student-60` identifiers. It does not use the application's private salt or store
raw session IDs/messages. `random.seed(7)` fixes the sample choices; UUID request
IDs and timestamps vary. Seeding is additive: a second run adds another 300
interactions, so use a fresh database for the exact-count check.

Measured fresh migrated database, after the two migration runs and one seed:

| Check | Result |
| --- | ---: |
| Migration versions | 2 |
| Interactions | 300 |
| Distinct request IDs | 300 |
| Hashed sessions | 59 |
| Feedback rows | 96 |
| FAQ rows | 0 |
| Foreign-key violations (`PRAGMA foreign_key_check`) | 0 |
| Raw `student-*` session IDs stored | 0 |

The database remains local under `.lab5-tmp`; it is not submission content.

## Schema compatibility and test evidence

Tests compare migrated table columns, primary keys, foreign keys, interaction
request-ID uniqueness, and lookup indexes with the repository contract. They
also exercise SQLModel writes, reopened reads and relationships without calling
`create_all` on the migrated database. Both fresh ORM-created and migrated
databases accept the 300-interaction seed, and repository statistics count all
300 rows. Feedback ratings and hashed session membership are checked.

Compatibility means the models can operate on the schema; it does not imply
identical DDL. In particular, the SQL migration includes a feedback-rating CHECK
constraint and the FAQ table; ORM `create_all` alone does not supply either.
Run migrations for the versioned schema.

| Check | Result |
| --- | --- |
| `python -m pip check` | No broken requirements |
| Ruff across src, tests, practice and scripts | Passed |
| Existing core/API regression suite | 55 passed |
| Configuration and migration/seed checks, excluding checker exercises | 9 passed |
| Focused existing R1 tests | 3 passed |
| Full suite on isolated base source `5056e0e` | 88 passed, 31 failed |
| Full suite on TV6 | 99 passed, 25 failed |
| `git diff --check` | Passed |

The base comparison explicitly sets PYTHONPATH to the extracted base's `src`
so subprocesses cannot accidentally import this branch's editable installation.
Six existing failures are resolved and five additional test cases pass. Remaining
failures: 10 API persistence cases, three R2 cases, 10 school SQL answers Q1-Q10,
and two D1 insertion cases. They are preexisting unfinished team work. The full
suite still exits nonzero; this report does not claim complete Lab 5 integration.
Starlette emits one upstream AnyIO deprecation warning.

Reproduce the passing focused checks:

```powershell
python scripts/check_lab5.py --baseline
python -m pytest -q tests/lab5/test_config.py tests/lab5/test_scripts.py -k "not checker" -p no:cacheprovider --basetemp=.lab5-tmp/tv6-focused-fresh
python -m pytest -q tests/lab5/test_db.py tests/lab5/test_repository.py -k "feedback_requires_existing or saved_feedback or unknown_request_does_not" -p no:cacheprovider --basetemp=.lab5-tmp/tv6-r1-fresh
```

Choose a new `--basetemp` path each time. For the entire team's completion check,
run `python scripts/check_lab5.py`; the remaining tasks must be finished before
that command can pass. Teammates review and merge the linked PR.
