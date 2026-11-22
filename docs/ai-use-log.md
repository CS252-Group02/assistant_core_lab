# AI use log

| Date | Contributor | Tool | Task | Retained output | Verification |
| --- | --- | --- | --- | --- | --- |
| 2026-11-14 | TV6 | OpenAI Codex | Database configuration, migration compatibility and synthetic seed verification | Environment-backed Settings; R1 feedback saving; additional configuration, migration and seed checks; reproduction evidence | 55 regression tests passed; 9 configuration/script checks and 3 focused R1 checks passed; full suite 99 passed / 25 unrelated failures. See `docs/lab5/tv6-verification.md`. |
| 2026-11-13 | nghiale29-coder (TV7) | OpenAI Codex | Strict SQL checker, bonus design review and submission evidence | Optional argparse strict mode; isolated CLI tests; English worksheet, Mermaid ER diagram, checker usage and demo/evidence documents | Measured checks and integration limitations are recorded in `docs/lab5/tv7-verification.md`. Existing answers, acceptance tests and TV1-TV6 implementation were not altered. |
| 2026-11-19 | TV6 | OpenAI Codex | Part F comparison | Supplied evaluator and 20-case fixture, completed worksheet, and run evidence | All three paths ran offline. RAG tests passed 15/15. See `docs/lab6/path_comparison.md`. |
| 2026-11-22 | TV2 | OpenAI Codex | Lab 7 L1 source display | Formatter, focused tests, and Streamlit caption evidence | Three formatter tests and three AppTest caption scenarios passed. Full suite recorded 155 passes and one pre-existing Lab 5 failure. See `docs/lab7/member2_sources.md`. |

The contributor should read the final diff, understand each retained change and
request TV1 review. Proposed privacy/retention policies are documented as
proposals; no automatic cleanup or unrelated database fixes are claimed.
