# TV7 review of TV6 — Lab 7 tests and usability coverage

Reviewed **2026-11-28**: [PR #44](https://github.com/CS252-Group02/assistant_core_lab/pull/44),
branch `test/lab07-tv6-Tests_and_Check`, head
`c7c869bffbc4a7ce3a2ce742dfc9dd63e92f84b4`. Its merge base is
`05996c8e6029c94b94cbb2b5fb183f551deb0f59`; current main is `41703b6`.
The PR is open, with five preparation commits and three files. TV7 submitted
no GitHub review/approval and changed none of TV6's files.

## Source fidelity and useful coverage

AST comparison confirms all **seven official test functions**, plus the supplied
client helper, are unchanged. TV6 adds multi-source ordering, degraded status,
escalation priority, timeout/429 messages, negative-vote payload, and feedback
HTTP/transport failure cases. Parameterization yields **18 executed cases**.
The MockTransport cases are deterministic and appropriately avoid live services.

The checklist is byte-identical to the pinned instructor Git file and all ten
items remain unchecked. Its LF SHA256 is
`46d7ee0b42b7bd7167b599f8424acda5e74cd48bf706317186949eb54f7a300b`.
The report's `38f28b...` checklist hash and `4ab21a...` original-test hash match
CRLF versions exactly; this is Windows line-ending normalization, not altered
requirements. The full supplied Lab 7 README, UI and worksheets were inspected;
no separate numbered D.4/E assignment handout exists in that repository snapshot.

## Executed checks

Environment, pinned overlay files and full-suite outputs are in
[integration verification](integration_verification.md). Additional raw output:
[TV6 review results](evidence/tv6-review-results.txt).

| Context / command | Actual result and interpretation |
| --- | --- |
| Exact TV6 head, `python -m pytest -q tests/test_ui.py -p no:cacheprovider --tb=short` | **1 collection error**, exit 2: `ModuleNotFoundError: No module named 'ui.api_client'`. Missing TV5 dependency on this stale branch. |
| Current main with TV6 test file selected by absolute path | **16 passed, 2 failed**, exit 1: `test_format_sources` and `test_format_multiple_sources` raise `NotImplementedError: L1`. TV2 formatter remains unmerged. |
| Temporary main + TV2/TV4/TV6 assembly, same focused command | **18 passed**, exit 0. TV3's existing L2 and TV5's merged client meet these assertions. |
| TV6 + supplied UI suite + TV2 sources + TV4 AppTest | **35 passed**, exit 0. Seven official cases overlap TV6's preserved starter coverage; this is not 35 distinct requirements. |
| Untouched main regression | **152 passed, 1 failed**, exit 1. |
| Temporary integrated regression | **187 passed, 1 failed**, exit 1; same failing node. |

Full regressions produced the same counts with both instructor and team
FastAPI/HTTPX dependency pins. The shared failure is
`tests/lab5/test_scripts.py::test_migrations_are_repeatable_and_preserve_data`
at line 63: `len(saved.feedback)` raises `TypeError: object of type 'Feedback'
has no len()`. It reproduces on untouched main, and earlier Lab 6 evidence also
records it. Likely cause: SQLAlchemy infers scalar cardinality for the explicit
`Interaction.feedback` relationship despite its list annotation. Hand off to
the Lab 5 model/repository owner (TV4, with TV6 migration-test coordination).
Do not weaken the test or silently classify the full suite as passing.

Sandbox TestClient attempts timed out at 20 seconds, exit 124; approved execution
outside the sandbox completed in approximately 6–7 seconds. The Starlette/AnyIO
`BlockingPortal` warning is an upstream deprecation, not a new Lab 7 failure.

To recreate the exact TV6-head check without changing a branch:

```bash
mkdir -p /tmp/lab07-tv6-review
git archive c7c869bffbc4a7ce3a2ce742dfc9dd63e92f84b4 | tar -x -C /tmp/lab07-tv6-review
cd /tmp/lab07-tv6-review
export PYTHONPATH=.:src:practice:/tmp
/tmp/lab07-venv/bin/python -m pytest -q tests/test_ui.py -p no:cacheprovider --tb=short
```

For the main-only dependency check, run from `/tmp/lab07-tv7-baseline` with the
same `PYTHONPATH`, selecting `/tmp/lab07-tv7-integration/tests/test_ui.py`.
For integrated checks, use the runbook's pinned assembly.

## Actionable findings and handoffs

| Priority | Finding / exact evidence | Owner and next action |
| --- | --- | --- |
| High | TV6's branch cannot collect; current main still fails L1. The report correctly declares verification pending. | TV1/TV2/TV5 integrate the app, formatter, root import setup and dependencies through normal reviews; TV6 reruns its tests on that exact integrated commit. Passing this scratch assembly does not complete PR #44 acceptance. |
| Medium | Client tests cannot verify rendered captions, history, session state or one-vote behavior. | TV6 incorporate/run TV4's existing `tests/test_ui_feedback.py` and TV2's `tests/test_ui_sources.py`; retain the browser scenarios. No need to rewrite teammate tests. |
| Medium | No HTTP-200 malformed-body coverage. Smoke probes against the real client raise `JSONDecodeError` for `not-json` and `KeyError: 'intent'` for `{"answer":"partial"}`. This can interrupt the UI. | TV5 decide/implement friendly invalid-response handling; TV6 add malformed JSON/missing-required-field cases after coordination. These are injected client-unit probes, not observed backend failures. |
| Medium | Source-ID assertions alone cannot establish study-answer completeness. The stub omits the card fee/time, and a compound question returns only the card answer. | RAG/stub owners (TV2/TV4; TV1 coordinates integration) agree acceptance for the chosen study provider. TV6 assert substantive facts or document these limitations; existing template mode passes the full-section API checks. TV7 retains the full observer answer key. |
| Low | `healthy()`, chat request method/body/session ID, positive-feedback payload, and the 2,000-character boundary are not directly asserted in TV6's suite. Successful parsing does not check all response metadata. | TV6 add focused cases for health 200/500/timeout, chat payload, source/status/path preservation, positive vote payload, and 2,000/2,001 boundaries if not covered elsewhere. Avoid duplicate tests. |
| Human-dependent | TV6's browser checklist, two-minute hallway session and full D.4/E sign-off are still pending in its own report. | TV6 review/repeat the evidence below on the final app, cross-check the course handout, conduct its own hallway session, and update only observed checklist items. TV7's separate ten-minute study is also pending. |

## Checklist cross-check from preliminary browser inspection

These are developer checks on a temporary assembly, not edits or ticks in
TV6's official worksheet:

| Official checklist area | Evidence / remaining qualification |
| --- | --- |
| Capabilities/examples | Visible on desktop; phone welcome includes a thesis example, with full example list behind the sidebar. |
| Empty/long input | Friendly whitespace and 2,001-character warnings observed; HTTP empty/long requests return 422. |
| Thinking indicator | Captured during real delayed-provider execution. |
| Sources | IDs and titles visible for both study answers; multiple-source formatting covered by unit tests. |
| Escalation | Football question gives Training Office I.101; flag precedence passes unit tests. |
| Backend unavailable | Page banner and chat failure shown after stopping the actual API. |
| Voting/thanks | Both real ratings stored; failure/retry and no duplicate submission across reruns verified. |
| AI disclosure | Visible in desktop sidebar and after opening phone sidebar; hidden on initial phone view. |
| Readability/labels | Body readable in inspection; faint captions/disclosure and emoji-only visible vote labels are study candidates, not a human-approved result. |
| Phone layout | 375 px, no horizontal overflow; wrapped sources, stacked controls and reachable sidebar; placeholder truncates. |

All ten genuine screenshots and browser events are indexed in
[release evidence](release_evidence.md). No external participant or hallway
observation has been supplied. Review disposition: **integration and human
verification remain required; no automatic approval or merge**.
