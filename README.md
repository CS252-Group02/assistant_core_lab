# Study Assistant - Lab 5 setup

This repository continues the team's Lab 4 API. Lab 5 adds SQL practice and SQLite
persistence. The setup and acceptance tests are ready for the team to implement
the remaining tasks. No CI workflow is required for this lab.

## Requirements

- Python **3.11** (recommended for the pinned starter dependencies).
- Git and a terminal. DB Browser for SQLite or a VS Code SQLite viewer is optional.
- No database server, Docker, real LLM key, or weather API connection is needed for tests.

The original environment on this machine uses Python 3.15; use the separate
`.venv-lab5` environment below instead of that `.venv`.

## Windows setup (PowerShell)

```powershell
py -3.11 -m venv .venv-lab5
.\.venv-lab5\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
Copy-Item .env.example .env
python scripts/check_lab5.py --baseline
```

Run the environment creation command once. On later visits, activate the existing
environment. Copy `.env.example` only when `.env` does not already exist, so local
settings are preserved. If PowerShell blocks activation, call
`.\.venv-lab5\Scripts\python.exe` in place of `python`; no policy change is needed.
In VS Code, select `.venv-lab5/Scripts/python.exe` as the Python interpreter.

If `py -3.11` is unavailable, install Python 3.11 before creating the environment.
The ignored `.lab5-tools` directory on the preparation machine is local tooling;
it is not needed by other members and is not part of the submission.

## macOS / Linux setup

```bash
python3.11 -m venv .venv-lab5
source .venv-lab5/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
cp .env.example .env
python scripts/check_lab5.py --baseline
```

## Local checks

```powershell
# Setup check: lint plus the existing core/API regression suite (must pass).
python scripts/check_lab5.py --baseline

# Completion check: lint plus every practice and Lab 5 acceptance test.
python scripts/check_lab5.py

# Optional: inspect the school database and the instructor's SQL score.
python practice/make_school_db.py
python practice/check.py
```

**The full suite is intentionally red until the team finishes the exercises.**
Failures must come from missing implementation, not missing dependencies or test
collection errors. No pending tests are skipped or marked xfail.

The SQL checker preserves the original score-only mode and supports optional
strict exit codes for automation:

```powershell
python practice/check.py
python practice/check.py --strict
python practice/check.py path/to/answers.sql --strict
```

Default mode exits 0 after scoring, even for missing/wrong answers or SQL errors.
Strict mode exits 0 only for full marks and 1 otherwise. Input/setup failures exit
1 in either mode; invalid command-line arguments exit 2. No SQL answers are
hardcoded in the checker. See [TV7 verification](docs/lab5/tv7-verification.md)
and the [submission/demo guide](docs/lab5/submission-evidence.md).

## Run the API

```powershell
python -m uvicorn assistant_api.main:create_app --factory --reload
```

Open `http://127.0.0.1:8000/docs`. During setup, the API still uses the Lab 4
in-memory feedback list. Repository integration remains unfinished. Configuration
now loads `DATABASE_URL` and `SESSION_SALT`; API repository wiring is a separate
team task. See [TV6 database verification](docs/lab5/tv6-verification.md) for
environment setup, repeatable migrations and the 300-interaction synthetic seed.

See [Lab 5 technical notes](docs/lab5/README.md) for supplied examples, test commands,
and the interfaces expected by the acceptance tests.

See [setup verification](docs/lab5/setup-verification.md) for the initial test
results and the expected unfinished-work failures.
