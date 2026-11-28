# TV7 — Lab 7 release evidence and handoff

**Status: preparation and preliminary technical evidence complete; final release
acceptance is pending.** No external participant has been observed, no
participant-based fix has been implemented, and no release tag has been created.

## Evidence index

| Evidence | Location / meaning |
| --- | --- |
| Official blank observation form | [Worksheet](../../worksheets/user_test_observations.md), copied verbatim; SHA256 `99717e3e03ab9a3137defb3bd3b06a12f7feb2bad28514208e3ff6c6554de3e6`. |
| Ten-minute study and observer-only answer key | [TV7 protocol](tv7_user_study.md). |
| Pinned sources, exact assembly/startup and measured checks | [Integration verification](integration_verification.md). |
| TV6 designated-reviewer findings and handoffs | [TV6 review](tv6_review.md). |
| Commit/PR and overlaid-file provenance | [Repository snapshot](evidence/repository-snapshot.json), [integration file hashes](evidence/integration-manifest.json). |
| Test counts, failures and environment locks | [Regression output](evidence/verification-results.txt), [TV6-specific output](evidence/tv6-review-results.txt), [course](evidence/course-environment.txt) / [team](evidence/team-environment.txt) dependency sets. |
| Actual answers and browser/database assertions | [API](evidence/api-results.json), [preflight](evidence/preflight-results.json), [browser](evidence/browser-results.json). |
| Existing retrieval-only study option | [Template-provider API check](evidence/template-study-results.json): complete KB sections, including card fee/time; no production change. |
| Screenshot integrity / capture context | [SHA256, dimensions, timestamps](evidence/screenshots.json), [supplemental capture record](evidence/supplemental-capture.json). |

All captured images below are genuine preliminary application captures. They
are **not a participant before/after pair**. Main browser run: real team API/UI,
team dependency pins, offline stub. A supplemental run recaptured phone/sidebar
and outage images after animations/rendering settled, using a separate disposable
DB. Fault-provider images use the documented delayed failing stub and actual
RAG fallback. No images were generated or edited.

| Screenshot | What it establishes |
| --- | --- |
| [Desktop start](screenshots/baseline-desktop-start.png) | Capability statement, examples, sidebar disclosure and input. |
| [Thesis](screenshots/baseline-thesis.png) | Threshold/GPA answer and `H26#5.3` caption. |
| [Card](screenshots/baseline-card.png) | Student Affairs I.102, `S26#3`, both voting controls; normal stub omits fee/time. |
| [Feedback failure](screenshots/baseline-feedback-failure.png) | Real backend stopped: error and retry controls remain. |
| [Backend down](screenshots/baseline-backend-down.png) | Connection banner and failed-chat message. |
| [Phone start](screenshots/baseline-phone-start.png) | Initial 375 px view with sidebar collapsed. |
| [Phone sidebar](screenshots/baseline-phone-sidebar.png) | Examples/disclosure reachable after opening sidebar. |
| [Phone card](screenshots/baseline-phone-card.png) | Wrapped sources and stacked controls at 375 px. |
| [Injected delay/loading](screenshots/fault-provider-loading.png) | Actual `Thinking…` indicator while the provider is delayed. |
| [Injected provider failure](screenshots/fault-provider-degraded.png) | Source fallback with the degraded explanation. |

## Release readiness

- [x] Fetch/inspect current main, teammate branches, recent commits, PRs and issues.
- [x] Import the instructor worksheet unchanged and prepare the external-study protocol.
- [x] Assemble compatible teammate work in isolation; record all sources/configuration.
- [x] Run API/UI, 35 UI cases, regression comparisons and real desktop/phone browser checks.
- [x] Capture genuine baseline images; keep developer findings separate from human evidence.
- [x] Review TV6 and document concrete coverage/dependency handoffs without editing its files.
- [ ] TV1 supplies/reconciles the production app and Streamlit setup; TV2/TV4/TV6 changes complete normal teammate review/integration.
- [ ] TV6 verifies the final integrated commit, updates its checklist, and completes its two-minute hallway test / course D.4/E checks.
- [ ] Team resolves or explicitly triages the existing Lab 5 ORM failure; current full suite is not green.
- [ ] Choose and record the study provider; verify answer completeness on the final build. The stub's first-sentence answer is incomplete; existing `LLM_PROVIDER=template` passes the full-section fact checks.
- [ ] TV7 conducts the ten-minute study with a non-team participant and records actual behavior.
- [ ] Relevant owner implements at least one change supported by an actual worksheet observation.
- [ ] TV7 links the fix commit and genuine same-scenario before/after captures, with relevant rerun results and teammate review.
- [ ] Release owner verifies final evidence and manually tags the approved merged release commit using the course/team's agreed tag name.

The main baseline has **152 passes / 1 failure**; the temporary integration has
**187 passes / the same failure**. TV6's 18 cases and TV4's seven AppTest cases
pass when integrated. These results support preparation, not a claim that the
unmerged main UI or final release is complete.

## Improvement candidates — hypotheses, not observed participant fixes

Choose only after the external study supplies a relevant observation. These
candidates have not been implemented in production by TV7.

| Candidate / relevant file | Responsible owner | Current behavior | Proposed change and expected benefit |
| --- | --- | --- | --- |
| AI disclosure visibility, `ui/app.py` | TV1; coordinate TV4 app reconciliation | Disclosure is in a collapsed sidebar on phone. | Place a short disclosure in the main initial view; users can identify the assistant without discovering the sidebar. |
| Source prominence, `ui/app.py` (rendering), `ui/logic.py` (wording) | TV1 / TV2 | Source IDs/titles appear as faint caption text. | Increase prominence with readable source text while preserving IDs/titles; users can locate the supporting rule. |
| Student-facing recovery, `ui/app.py` | TV1 / TV5 | Backend-down banner tells students to run a uvicorn command. | Explain temporary unavailability, retry and staff contact in student language; students know their next action. |
| Visible voting labels, `ui/app.py` feedback block | TV4, with TV1 | Emoji buttons have helpful tooltips, but only icons are visible; controls stack on phones. | If users misinterpret them, add short helpful/not-helpful labels and verify fit; intent is clearer. |
| Complete policy answers, `src/assistant_core/llm.py`, service/RAG behavior | Lab 6 grounding/fallback owners TV2/TV4; TV1 coordinates | Stub takes first source sentence, omits card fee/time and answers only one part of a compound task. | Agree full-answer behavior/provider; preserve source grounding and state assumptions. Existing template mode already returns the complete section. This requires owner coordination, not a TV7 UI patch. |

The existing ORM failure belongs to the Lab 5 model/repository owner (TV4), with
TV6 migration-test coordination. Invalid HTTP-200 response handling belongs to
TV5, with TV6 coverage. Details and reproduction are in the review. Neither is
attributed to an external user.

## What TV7 personally completes next

1. Review these five commits and create the PR manually. Coordinate TV1's app,
   TV2's L1, TV4's F1 and TV6's tests/checklist through the team's usual reviews;
   this branch contains documentation/evidence only and cannot itself make main
   runnable. Do not merge unapproved teammate branches.
2. Agree the exact build/provider for the study. To use the existing complete
   source-section option, set `LLM_PROVIDER=template` in the **backend** terminal
   instead of `stub`, restart it and check both questions. This was verified over
   HTTP, not used for the baseline browser screenshots. Capture a fresh baseline
   on the actual selected build; keep the provider unchanged across before/after.
3. Recruit one participant outside the team, obtain consent, record only their
   first name/date, and run the protocol's exact task for ten minutes without
   helping. Record timestamped actions/statements, expectations, misunderstandings,
   UI causes and outcomes in the supplied worksheet. Do not show the answer key.
4. Discuss one actual observation with the relevant owner and agree a concrete
   fix and acceptance check. Have that owner implement/review the change. Add its
   real commit link to the worksheet; a preliminary candidate alone does not count.
5. Capture the original observed problem **before** the fix and repeat the same
   scenario **after** it at the same viewport/provider. Suggested future filenames:
   `study-<actual-date>-before.png` and `study-<actual-date>-after.png`. No such
   files exist yet. Record build hashes and expected/actual behavior; run affected
   checks and coordinate final regression/checklist verification with TV6.
6. Submit the completed worksheet, consent-safe notes, fix link and paired images
   in a follow-up evidence change. Replace pending statuses only with actual
   evidence and obtain teammate review. Have the release owner fetch the final
   merged commit, confirm readiness and publish the agreed release tag manually.
   No tag or release publication was performed here.

AI-use disclosure: OpenAI Codex assisted with repository/material inspection,
isolated integration, automated verification, preliminary UI inspection and
these English reports. No AI-generated participant behavior, identity or study
outcome is included. TV7 must review and understand the retained evidence.
