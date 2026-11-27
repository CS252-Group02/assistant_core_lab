# Lab 07 - TV4 feedback UI (F1)

## Implemented behavior

The feedback block in `ui/app.py` now renders both voting buttons for an assistant answer with an unrated request ID. The positive button uses `up{i}` and sends rating `1`; the negative button uses `down{i}` and sends rating `-1`. The index gives each button a unique key when the history contains several answers.

Both buttons use the boolean returned by TV5's `AssistantClient.send_feedback`. Only a successful response adds the request ID to `st.session_state.rated`, removes that answer's controls immediately, and shows the appropriate confirmation:

- Positive: `Thanks for your feedback!`
- Negative: `Thanks — we will look at this answer.`

When sending fails, the app shows `Your feedback was not saved. Please try again.`, keeps the answer unrated, and leaves both buttons available for an explicit retry. An ordinary rerun does not submit another vote. The existing HTTP client handles HTTP and connection failures; the feedback UI does not change the API contract or backend persistence.

## Source and integration scope

At preparation time, team `main` at `05996c8e6029c94b94cbb2b5fb183f551deb0f59` had no `ui/app.py` or `ui/api_client.py`. The app in this contribution is therefore a candidate based on the [pinned instructor starter](https://github.com/CSC10014-at-fit-hcmus/public_materials/blob/397639e11ac3bb47516d5de8211ccbfb3955794a/lab07/starter/ui/app.py), whose SHA256 is `12fdb5fb0e8596c1ca7548ea4fc67334d3bb699811343d93857823405a87b8a1`.

Only the feedback block differs from that pinned app. Its imports, session initialization, sidebar, answer/source/status rendering, and question handling are preserved. `tv4_feedback.patch` contains the narrow diff for TV1 to apply after the UI foundation is available, rather than replacing TV1's app with this candidate if they have made other changes.

For verification only, a separate local scratch runtime combined:

- This TV4 app candidate.
- The real team FastAPI/backend code at `05996c8`.
- TV5's HTTP client from `feat/lab08-tv5-http-be`, commit `cf488e3bb1db11e7b1afdb94fb112cfdc74c55a1` ([PR #43](https://github.com/CS252-Group02/assistant_core_lab/pull/43)).
- The `format_sources` function from TV2's `test/lab07-tv2-source-display`, commit `4c6850e81e44fe0bc094818ba5731d772edbae83` ([PR #41](https://github.com/CS252-Group02/assistant_core_lab/pull/41)), combined with the status-note implementation already on `main`.
- The instructor's empty `ui/__init__.py` in that scratch runtime.

Those teammate-owned modules and dependency files are not included in the TV4 changes. TV1 supplies the application foundation and Streamlit setup; TV5 reviews this feedback change and provides the HTTP client. TV6 can reuse the focused tests alongside its shared UI suite.

## Automated verification - November 27, 2026

Environment: Windows, isolated Python 3.11.9, Streamlit 1.39.0, HTTPX 0.27.2, FastAPI 0.115.0, SQLModel 0.0.22, and pytest 8.3.3. The course's pinned dependencies were installed in a separate local runtime without changing the project's shared requirements.

`tests/test_ui_feedback.py` executes the actual candidate app with Streamlit AppTest. Only the HTTP client is mocked in these tests.

| Check | Result |
|---|---|
| Positive vote: correct request ID and rating `1`, confirmation, immediate control removal, unchanged session/history across reruns | Passed |
| Negative vote: correct request ID and rating `-1`, confirmation, immediate control removal, no duplicate submission on reruns | Passed |
| Failed positive vote: error, no success toast, remains unrated, successful explicit retry | Passed |
| Failed negative vote: error, no success toast, remains unrated, successful explicit retry | Passed |
| Several answers: unique keys, independent request IDs, one rating per answer | Passed |
| Welcome/error messages without request IDs: no voting controls or submissions | Passed |
| Previously rated request: no controls or automatic resubmission | Passed |

Results: **7 focused AppTest cases passed**. Running those tests together with the instructor's seven client/logic tests produced **14 passed**. Ruff passed for the app and focused tests; `pip check` found no broken requirements. This is scoped TV4 verification, not a claim that the full team regression suite has been executed.

After TV1/TV5 integrate their modules and dependencies, the focused checks run from the repository root:

```powershell
python -m pytest -q tests/test_ui_feedback.py
python -m ruff check ui/app.py tests/test_ui_feedback.py
```

The existing TV6 UI suite can then be run with `python -m pytest -q tests/test_ui.py` after that branch is integrated.

## Real-browser and persistence verification

Headless Chrome ran the Streamlit page against the real team FastAPI backend, using a new isolated SQLite database with synthetic questions. These were real browser clicks and HTTP requests, not mocked feedback responses.

1. Submitted `Tuition for 18 credits and 2 retake` and clicked the negative button. The backend stored rating `-1`; the negative confirmation appeared and both buttons disappeared.
2. Asked `Where is the library?` and clicked the positive button. A different request ID received rating `1`; its confirmation appeared and its buttons disappeared independently.
3. Asked `I lost my student card`, stopped the backend, and clicked the negative button. The error appeared, the controls remained, and the database stayed at two feedback records.
4. Restarted the backend with the same database and explicitly retried. The third record was stored with rating `-1`.
5. Triggered two normal Streamlit browser reruns. The database still contained exactly three records with ratings `[-1, 1, -1]`, and the rated answers' controls remained hidden.

Screenshots captured from that browser session:

- [Negative vote saved](screenshots/feedback_negative.png)
- [Positive vote saved](screenshots/feedback_positive.png)
- [Backend unavailable: vote not saved, retry remains available](screenshots/feedback_failure.png)

The local test servers were stopped after verification. Repeat the checks on the team's integrated TV1 app before merging if its history or feedback layout differs. The rated state prevents repeated clicks within the current Streamlit session; it is not a backend guarantee of exactly-once delivery across new sessions or an ambiguous network failure after a database commit.
