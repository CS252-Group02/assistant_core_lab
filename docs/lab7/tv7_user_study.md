# TV7 — ten-minute external user study

Status: **prepared; no external participant has been observed**. Automated and
developer inspection results belong in [integration verification](integration_verification.md).
Use the [official observation worksheet](../../worksheets/user_test_observations.md)
for the real study; it is intentionally blank and copied verbatim from instructor
commit `397639e11ac3bb47516d5de8211ccbfb3955794a`.

## Prepare before the participant arrives

1. Recruit one person outside this team. Record only their first name and date
   on the worksheet, after obtaining their consent to notes and any screenshots.
   Use synthetic questions; do not enter student IDs or private academic records.
2. Follow the [integration runbook](integration_verification.md) to start the API
   and UI with the agreed offline provider and a disposable database. The existing
   template mode returns the complete source sections; record the choice. Verify `/health`,
   source captions, and voting. Record the exact integrated commits, provider,
   viewport, browser, date and checklist result with the session evidence.
3. Have TV6 verify its usability checklist on this build. Use a fresh Streamlit
   session with no previous questions or votes. Keep this observer answer key
   and other team documentation out of the participant's view.
4. Prepare a ten-minute timer, the worksheet and a timestamped note sheet.
   Capture a baseline screenshot of the actual build. Do not use a different
   mocked build or the screenshots from preliminary developer inspection as
   participant evidence.

## Read to the participant

"Please use this application for up to ten minutes. Find out if you can register
your thesis with 118 credits, and where to replace a lost student card. You may
say what you are thinking as you go. I will watch without helping or explaining
how the application works."

Start the timer after reading. Do not point to the sidebar, suggest queries,
reveal the answer key, correct a misunderstanding, or demonstrate the controls.
If the participant asks for help, record the request without giving directions.
They may stop at any time. Record an environmental failure if it prevents the
task; do not silently repair the app and call the task an unassisted success.

## Observe for ten minutes

- Minutes 0–2: record the first action, what they appear to look for, typed
  queries, spontaneous statements and any requests for help.
- Minutes 2–8: record navigation, submitted questions, answer reading, source
  discovery, scrolling, waiting, repeated actions, voting and recovery attempts.
  Use elapsed times; distinguish verbatim statements from observer inference.
- Minutes 8–10: continue observing without steering. At the end ask neutrally:
  "What did you conclude?" and "What did you expect when that happened?"
  Record their own explanation and whether they located the sources.

For each worksheet row, link a timestamp/action or exact statement to the
participant's expected behavior, actual outcome, plausible UI cause and a fix
idea. Mark inferred expectations as inferred until confirmed in the debrief.
Keep technical failures separate from confusion. Do not invent observations
if the participant finishes early or fewer than three problems occur; describe
what actually happened and leave unused rows blank.

## Observer-only answer key and evaluation

Verified against instructor `lab07/starter/data/kb/` and the team's matching KB:

| Task | Required conclusion | Source |
| --- | --- | --- |
| Thesis with 118 accumulated credits | Not eligible: at least **120 credits** and cumulative **GPA ≥ 2.0** are required. Do not invent the student's GPA. | `H26#5.3`, handbook section 5.3 |
| Replace a lost student card | **Student Affairs, room I.102**; **50,000 VND**; **three working days**. | `S26#3`, services section 3 |

For each task record completion time, unassisted correct/partial/incorrect/not
completed, the participant's stated conclusion, and whether they found the ID
and title. Credit a source caption separately from factual completeness: showing
`S26#3` alone does not establish that the answer includes the fee and time.
Record whether the thesis ineligibility conclusion was explicit or the
participant inferred it from a quoted rule. Do not coach them to make it.

## Select, implement and verify one observed improvement

After the session, choose one actual worksheet observation with the relevant
file owner. Document why that observation supports the change, the file/owner,
expected benefit and a concrete acceptance check. Preliminary candidates are
listed in [release evidence](release_evidence.md); they are hypotheses only.
Coordinate implementation in the owner's branch, preserve the API contract,
and run the affected UI and regression checks. TV7 does not own their UI code.

Capture the real before and after states at the same viewport using the same
question and provider. Label the builds and commits, link the owner's fix commit
in the worksheet, and explain the observed problem and resulting behavior.
Do not relabel a preliminary screenshot as a participant capture or fabricate
an after image. Link the completed worksheet, consent-safe observation notes,
paired screenshots, fix commit and rerun results from the release evidence.
Have a teammate review the evidence before the release owner creates a tag.
