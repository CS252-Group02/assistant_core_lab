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
