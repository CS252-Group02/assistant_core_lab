# Lab 7 — TV6 automated tests and browser checks

## Scope

TV6 owns `tests/test_ui.py`, `worksheets/usability_checklist.md`, and this
verification record. Use `D:/Lab_CT/public_materials/lab07/` as the supplied
source. Preserve the starter tests and extend coverage in the same test file.
The usability checklist is copied unchanged from the supplied worksheet.

Do not modify UI implementation, backend code, dependencies, configuration,
or TV7's external-user observation worksheet. Report implementation failures
to the relevant owner for correction.

## Automated coverage prepared

The starter tests cover successful chat, backend connection failure, HTTP 422
and 500 responses, positive feedback, input validation, empty/single sources,
and normal/escalation status notes.

Additional tests cover:

- Multiple sources: retain IDs, titles, order, and semicolon separators.
- Degraded status: show the supplied fallback explanation.
- Both status flags: escalation takes priority over degraded fallback.
- Chat timeout: return the supplied retry message instead of propagating an exception.
- HTTP 429: return the supplied rate-limit message.
- Negative feedback: send one POST to `/v1/feedback` with the request ID,
  rating `-1`, and the default null comment.
- Feedback HTTP failures (400, 429, 500), connection errors, and read timeouts:
  return `False`.

HTTP cases use `httpx.MockTransport`; they do not require a running server.
They still need the actual `ui.api_client` and `ui.logic` modules to import.
These unit tests do not establish browser behavior or feedback persistence.

## Browser verification plan — not executed

After the integrated application is available, start the backend and UI using
the instructions maintained by TV1. Use the approved Lab 7 D.4/E instructions
as the source of truth for scenarios and hallway-test procedure. The list
below is preparation, not a claim that every D.4 scenario has been identified.

| Area | Planned check | Status |
| --- | --- | --- |
| First screen | Capabilities, examples, and AI disclosure are visible. | Pending |
| Validation | Empty/too-long input produces friendly feedback without a crash. | Pending |
| Waiting/history | Loading indicator appears; session and history survive reruns. | Pending |
| Sources | Document answers show source IDs and titles, including multiple sources. | Pending |
| Status | Normal, degraded, and escalation states display correctly under the answer; escalation wins when both flags are true. | Pending |
| Backend errors | Disconnection, timeout, validation errors, rate limits, and server failures give understandable feedback. | Pending |
| Voting | Both buttons send the intended rating for the correct answer and show confirmation on success; reruns do not resend. | Pending |
| Feedback failure | Observe failure handling with TV4/TV5; do not mistake a failed submission for a successful persisted rating. | Pending |
| Phone width | At a narrow viewport (for example 375 px), inspect readable text, source wrapping, input, sidebar access, and voting controls. | Pending |
| Hallway test | Conduct the two-minute test in section E and record observed actions, confusion, and outcomes. | Pending |
| D.4 completeness | Cross-check and execute every scenario in the full assignment. | Pending |

For each executed check, record the date, integrated commit, environment,
steps, expected/actual behavior, and any failure reproduction details here.
Tick `worksheets/usability_checklist.md` only after observing the behavior.
TV7 owns the separate ten-minute external-user study and its release evidence;
TV6 reviews that evidence as assigned.

## Preparation record — 2026-11-24

This batch prepares tests and documentation only, as requested. No functional
tests, pytest collection, regression suite, backend calls, browser checks, or
human usability sessions were run. No test pass result is claimed.

Static checks performed:

- The initial copied `tests/test_ui.py` matched the starter's SHA256 before
  adding coverage: `4AB21A8D395FA57662349E7E71F36875256364D2AF3D35B680DBC10FE8C2D141`.
- The final test file preserves all supplied test functions and adds cases
  against the supplied client/logic interfaces.
- Python `ast.parse` accepted the test file without importing or executing it.
- `git diff --check` and staged diff checks reported no whitespace errors.
- The checklist matches the supplied worksheet's SHA256:
  `38F28BEF2B4DAC50866B8B73F8D1C3E0D32042A756B24EB35D35548EC36F62E1`.
  All ten checklist items remain unchecked.
- Tracked changes in these five commits are limited to the three TV6 files.

Preparation commits:

1. `9beaeea` — Copy the supplied UI tests unchanged.
2. `d3500e0` — Add multiple-source and status-priority tests.
3. `c31507f` — Add timeout, rate-limit, and feedback-failure tests.
4. `39aa7fe` — Add the checklist and browser verification plan.
5. `docs(lab7): document pending verification and team handoff` — Record pending
   checks, integration dependencies, and the handoff below.

## Pending integration and ownership

The following describes this branch at preparation time, not the live status
of remote pull requests:

| Dependency / finding | Owner and handoff |
| --- | --- |
| `ui/api_client.py` is absent; test imports depend on `AssistantClient` and `ChatResult`. | TV5 supplies the client; report HTTP mapping, payload, and feedback-return failures to TV5. |
| `ui/logic.py` exists, but `format_sources()` still contains TODO L1. | TV2 supplies formatting; report source-display failures to TV2. |
| `status_note()` is already implemented in the local branch. | Run prepared status tests after integration; report status/priority failures to TV3. |
| `ui/app.py` and `ui/__init__.py` are absent; root import-path configuration differs from the starter. | TV1 handles UI foundation, setup, and configuration; do not change those files in this task. |
| Feedback rendering, rated-state tracking, and rerun behavior require a runnable app. | TV4 owns the feedback block; coordinate API/failure handling with TV5. |
| TV7's external-user study and release evidence are not part of this test preparation. | Review TV7's evidence when it is available; keep the two-minute TV6 hallway test separate. |

Do not copy teammates' UI files, merge their implementation into this task,
skip failing tests, or change expected behavior just to obtain a pass.
Missing dependencies are pending integration, not successful validation.

## Commands and evidence to record after integration

After the team's PRs are merged, update this branch from the team's agreed
integration branch. Use the configured project Python environment and run from
the repository root:

```powershell
python -m pytest -q tests/test_ui.py
python -m pytest -q
```

If `ui` imports fail, report the exact error to TV1/TV5 as appropriate rather
than editing shared configuration or introducing substitute modules.

Record the selected test count, pass/fail/error counts, exact command, and
integrated commit here. For failures, include the failing test, expected and
actual behavior, and responsible owner. After owners fix issues, rerun the
affected tests and regression checks as needed.

Then execute the full D.4 scenarios, the phone-width check, the checklist,
and section E's two-minute hallway test. Record observations and only then
tick confirmed checklist items. Add the actual results in a follow-up commit.

Current acceptance status: **pending**. Five preparation commits do not mean
TV6's automated or browser verification requirements have been completed.
