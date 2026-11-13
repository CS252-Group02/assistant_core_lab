# Setup verification

Verified on November 13, 2026, using Python 3.11 on Windows.

| Check | Result |
| --- | --- |
| Fresh source snapshot with no sibling public-materials directory | Passed |
| New virtual environment, requirements installation, editable package installation | Passed |
| `python -m pip check` in the fresh environment | No broken requirements |
| Ruff across src, tests, practice, and scripts | Passed |
| Existing core/API regression suite | 55 passed |
| Full test collection | 111 collected, no collection errors |
| Full suite execution | 67 passed, 44 failed, no fixture/setup errors or skipped tests |

The 44 failures are expected in the initial setup: unanswered SQL, unfinished D1-D3 and
R1-R2, missing DB settings, API persistence integration, and checker strict mode.
Migration/seed integration tests also fail until R1 is implemented. These failures
identify unfinished exercises and integrations, not completed features.

Starlette emits an upstream AnyIO deprecation warning; it does not fail tests.
The restricted agent sandbox blocks pytest temporary-directory access, so the
successful execution checks were run outside that restriction. Ordinary team
terminals do not use this agent-specific sandbox.

The clean-source check installed dependencies into a new environment and ran the
baseline and full test collection there. The full red/green suite was executed
in the main Lab 5 environment. No exercise solutions were filled in to produce
these results.

## Reproduce

Follow the root README, then run:

```powershell
python -m pip check
python scripts/check_lab5.py --baseline
python scripts/check_lab5.py
```

The baseline command must exit 0. The full command must exit nonzero until all
implementation work is complete. At completion, both must exit 0.
