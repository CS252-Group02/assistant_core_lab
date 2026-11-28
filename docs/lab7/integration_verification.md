# TV7 — integration and preliminary verification

Executed on **2026-11-28**, using synthetic questions only. This is automated
and developer-led verification, **not an external user study**. The study
[protocol and answer key](tv7_user_study.md) define the human acceptance checks.

## Repository and source snapshot

The original checkout was clean on `main`. `git fetch origin --prune` completed
before branching. The TV7 branch starts at the latest fetched `origin/main`,
`41703b6d474b561ad82173f1cb582bb05357ebce`. Recent history includes merged Lab 6
RAG/evaluation work, TV3 status notes (PR #39), and TV5 HTTP client (PR #43).
Lab 5/6 evidence reports were read to retain measured-results, reproduction,
known-failure and pending-acceptance conventions. The root README still describes
an older Lab 5 setup; it is not a reliable description of current API persistence.

| Source | Pinned commit | Integration use / current status |
| --- | --- | --- |
| Instructor `public_materials` | `397639e11ac3bb47516d5de8211ccbfb3955794a` | `lab07/` starter README, UI, requirements, pyproject, tests, worksheets and KB inspected. |
| Team main | `41703b6d474b561ad82173f1cb582bb05357ebce` | Backend, DB, RAG, KB, configuration and regression baseline kept intact. |
| TV1 | No app implementation found in fetched branches/history | Foundation reused from the instructor-based TV4 app; TV1 must integrate the production app and dependencies. |
| TV2, [PR #41](https://github.com/CS252-Group02/assistant_core_lab/pull/41) | `4c6850e81e44fe0bc094818ba5731d772edbae83` | Unmerged `ui/logic.py` and `tests/test_ui_sources.py` copied into temporary worktree. |
| TV3, merged PR #39 | `47690a21c9a055875ea79bf7c135917dbd41ea78` | L2 already on main. AST comparison confirms TV2's copied `status_note` is identical. |
| TV4, [PR #47](https://github.com/CS252-Group02/assistant_core_lab/pull/47) | `d12d8d828b381aec536dad0e0882cfe7502c9709` | Unmerged `ui/app.py` and `tests/test_ui_feedback.py` reused. PR has a TV5 approval; no merge performed. |
| TV5, merged PR #43 | `cf488e3bb1db11e7b1afdb94fb112cfdc74c55a1` | `ui/api_client.py` already on main; no replacement needed. |
| TV6, [PR #44](https://github.com/CS252-Group02/assistant_core_lab/pull/44) | `c7c869bffbc4a7ce3a2ce742dfc9dd63e92f84b4` | Unmerged `tests/test_ui.py` and checklist copied only into temporary worktree. [Review](tv6_review.md). |

PR #41, #44 and #47 were open at inspection; #44 was ready for review, not draft.
Issues #40, #42, #45 and #46 and the recent PR discussions were inspected.
No PR approval, comment, merge, release or tag was submitted by this task.
No teammate branch was merged into main or the five-commit TV7 branch.

## Recreate the temporary assembly

Run from a clone containing the fetched team commits. Use fresh `/tmp` paths if
these already exist. The actual worktree is `/tmp/lab07-tv7-integration` at the
pinned main commit, with only the file overlays below. This is a file assembly,
not a merge of branch histories.

```bash
git fetch origin --prune
git clone --depth 1 https://github.com/CSC10014-at-fit-hcmus/public_materials.git /tmp/lab07-official
git -C /tmp/lab07-official checkout 397639e11ac3bb47516d5de8211ccbfb3955794a
git worktree add --detach /tmp/lab07-tv7-integration 41703b6d474b561ad82173f1cb582bb05357ebce
git show 4c6850e81e44fe0bc094818ba5731d772edbae83:ui/logic.py > /tmp/lab07-tv7-integration/ui/logic.py
git show 4c6850e81e44fe0bc094818ba5731d772edbae83:tests/test_ui_sources.py > /tmp/lab07-tv7-integration/tests/test_ui_sources.py
git show d12d8d828b381aec536dad0e0882cfe7502c9709:ui/app.py > /tmp/lab07-tv7-integration/ui/app.py
git show d12d8d828b381aec536dad0e0882cfe7502c9709:tests/test_ui_feedback.py > /tmp/lab07-tv7-integration/tests/test_ui_feedback.py
git show c7c869bffbc4a7ce3a2ce742dfc9dd63e92f84b4:tests/test_ui.py > /tmp/lab07-tv7-integration/tests/test_ui.py
git show c7c869bffbc4a7ce3a2ce742dfc9dd63e92f84b4:worksheets/usability_checklist.md > /tmp/lab07-tv7-integration/worksheets/usability_checklist.md
cp /tmp/lab07-official/lab07/starter/ui/__init__.py /tmp/lab07-tv7-integration/ui/__init__.py
cp /tmp/lab07-official/lab07/starter/tests/test_ui.py /tmp/lab07-tv7-integration/tests/test_ui_official.py
```

Only `ui/logic.py` differs among the main worktree's tracked files; the other
assembly files are additions. No backend, database model, API contract, RAG,
production configuration, requirements or pyproject file was changed.
`starter/ui/app.py` supplies TV4's foundation; its only functional difference
is TV4's feedback block. L1/L2/F1 all use teammate implementations; no temporary
TODO implementation was needed. The instructor's `ui/api_client.py`, `logic.py`
and `pyproject.toml` were references, rather than replacements for team work.
The official usability checklist remains unchecked and owned by TV6.

## Python, dependencies and startup

Linux x86_64; isolated **CPython 3.11.18**, Streamlit **1.39.0**, pytest **8.3.3**,
SQLModel **0.0.22**, Playwright **1.58.0**, system Brave/Chromium engine
**155.0.8059.80**. Initial verification used the instructor pins
(FastAPI 0.115.0 / HTTPX 0.27.2). Both regression suites were repeated with
team pins (FastAPI 0.115.14 / HTTPX 0.28.1 / Starlette 0.46.2); final screenshots
and browser results use those team pins. Both environments passed `pip check`.
Exact transitive versions: [course](evidence/course-environment.txt),
[team](evidence/team-environment.txt).

Only Python 3.14 was installed initially. Actual provisioning commands:

```bash
python3 -m pip install --target /tmp/lab07-tools uv
/tmp/lab07-tools/bin/uv python install 3.11 --install-dir /tmp/lab07-python --no-bin --cache-dir /tmp/lab07-uv-cache
/tmp/lab07-python/cpython-3.11-linux-x86_64-gnu/bin/python3.11 -m venv /tmp/lab07-venv
/tmp/lab07-venv/bin/python -m pip install -r /tmp/lab07-official/lab07/starter/requirements.txt playwright==1.58.0
# After recording the course-pin run, retain Streamlit and install the team pins:
/tmp/lab07-venv/bin/python -m pip install -r /tmp/lab07-tv7-integration/requirements.txt
/tmp/lab07-venv/bin/python -m pip check
```

No editable installation or shared dependency-file replacement was necessary;
explicit `PYTHONPATH` includes the root as in the official pytest configuration.
For the recorded exact environment, install `evidence/team-environment.txt`
from this TV7 checkout into a fresh Python 3.11 environment.

Actual normal browser configuration (put these exports in both terminals):

```bash
cd /tmp/lab07-tv7-integration
export PYTHONPATH=.:src:practice:/tmp
export LLM_PROVIDER=stub
export DATABASE_URL=sqlite:////tmp/lab07-tv7-browser-team.db
export SESSION_SALT=tv7-disposable-verification-only
export RATE_LIMIT_PER_MIN=300
export ASSISTANT_API_URL=http://127.0.0.1:8000
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
# Terminal 1:
/tmp/lab07-venv/bin/python -m uvicorn assistant_api.main:create_app --factory --host 127.0.0.1 --port 8000
# Terminal 2, after repeating the exports above:
/tmp/lab07-venv/bin/python -m streamlit run ui/app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --server.fileWatcherType none
```

Data/KB paths remain the main defaults (`data`, `data/kb`, BM25, min score 2.0,
`answer_v1`). No LLM credentials or weather calls were used. Salt above is a
public disposable-test value. For repeat runs choose a new database filename;
do not reuse valuable data. Tests used separate baseline/integration databases,
pytest temporary databases, and `/tmp/lab07-tv7-http.db` for HTTP checks. Supplemental captures used
`/tmp/lab07-tv7-screenshot-check.db`; template checks used
`/tmp/lab07-tv7-template.db`.
Normal UI chat/rated state persists across Streamlit reruns in the same session;
page reload/new-browser persistence is not promised or asserted.

## Actual verification

| Check | Measured result |
| --- | --- |
| `/health`, Streamlit `/_stcore/health` | HTTP 200; API `status=ok`, version `1.0.0`; UI `ok`. |
| UI unit/AppTest suites | **35 passed**: TV6 18, official 7, TV2 3, TV4 7. All are included in the full integrated result below. |
| Untouched main full suite | **152 passed, 1 failed** with either dependency set. |
| Temporary integrated full suite | **187 passed, 1 failed** with either dependency set; same failure as main. |
| Study questions over HTTP and in browser | Both 200; IDs/titles `H26#5.3` and `S26#3` correctly displayed. Content limitations below. |
| Unknown question | Football question abstains, with Training Office I.101 escalation and no sources. |
| Degraded/provider failure | Real RAG fallback quotes the source and shows TV3's explanatory note. |
| History/session | Both Q/A pairs survive two actual Streamlit menu reruns; same database session, five chat blocks, no duplicate feedback. TV4 AppTest also checks session ID and complete message equality. |
| Positive / negative votes | Real clicks persist `1` and `-1`, show distinct thanks toasts and remove controls for that answer. |
| Feedback outage/recovery | Stop backend; failed vote shows error, retains buttons and does not increase DB count. Restart same DB, explicitly retry; one new `-1` row. Final ratings `[1, -1, -1]`. |
| Backend failure | Failed chat shows `Cannot reach the assistant. Is the backend running?`; page shows backend-unreachable banner. |
| Loading | Actual `Thinking…` spinner captured during delayed failing-provider request. |
| Input | Whitespace and 2,001-character input show friendly warnings; no message/history addition. API empty/2,001-character requests return 422. |
| Phone, 375 × 812 | No horizontal overflow (document width 375); sources wrap, input and both vote buttons fit. Sidebar disclosure is reachable by opening the collapsed sidebar. |
| Desktop, 1280 × 1000 | Answer/source hierarchy and controls visually inspected; body text readable, caption/disclosure contrast warrants attention. No formal accessibility audit claimed. |

Raw [browser events](evidence/browser-results.json), [API responses](evidence/api-results.json),
[direct preflight responses](evidence/preflight-results.json), and
[test output](evidence/verification-results.txt) retain actual evidence.

Commands: from each applicable checkout with `PYTHONPATH=.:src:practice:/tmp`,
`LLM_PROVIDER=stub`, and a separate `DATABASE_URL`, run:

```bash
/tmp/lab07-venv/bin/python -m pytest -q tests/test_ui.py tests/test_ui_official.py tests/test_ui_sources.py tests/test_ui_feedback.py -p no:cacheprovider --tb=short
/tmp/lab07-venv/bin/python -m pytest -q -p no:cacheprovider --tb=short
```

Untouched main was extracted with `git archive 41703b6d474b561ad82173f1cb582bb05357ebce`
into `/tmp/lab07-tv7-baseline`. Its full suite uses only its existing files.
Failure in both: `tests/lab5/test_scripts.py:63`,
`test_migrations_are_repeatable_and_preserve_data`: `len(saved.feedback)` raises
`TypeError: object of type 'Feedback' has no len()`. This confirms an existing
ORM relationship problem, not a Lab 7 regression. One Starlette/AnyIO
`BlockingPortal` deprecation warning also occurs in each full run.

## Browser method and fault configuration

Playwright drove the actual page, textarea, voting controls and Streamlit
`stMainMenu` → `Rerun` command. It asserted rendered source/status/error text,
waited for message counts and spinner completion, and queried the isolated
SQLite database after votes/reruns. No chat responses were mocked in browser
verification. Screenshots are raw Playwright `page.screenshot(full_page=True)`
captures, without compositing or annotation; capture metadata and SHA256 values
are in the [screenshot manifest](evidence/screenshots.json).

For degraded/loading screenshots only, `/tmp/lab07_fault_app.py` built the same
real service with `load_settings(env_file=None)` and replaced `service.rag.llm`
with a subclass of the team's `StubLLM(fail=True)` whose `complete(prompt)` sleeps
one second then calls `super().complete(prompt)`. This delays each of the normal
two attempts and triggers the existing fallback. The API uses the unchanged
`create_app(settings=settings, service=service)` factory, on port 8001 with
`sqlite:////tmp/lab07-tv7-fault-team.db`. A second unchanged Streamlit app on 8502
sets `ASSISTANT_API_URL=http://127.0.0.1:8001`. No API response was fabricated.

Scratch automation: `/tmp/lab07-verify-browser.py`, `/tmp/lab07-http-verify.py`,
`/tmp/lab07-preflight.py`, fault factory and runtime exports remain outside the
TV7 branch. All test servers/browser processes launched by the harness were
stopped after capture. `/tmp/lab07-phone-capture.py` recaptured the phone/sidebar
and two outage images after a one-second render/animation settle; its
[supplemental record](evidence/supplemental-capture.json) confirms zero saved
feedback during the outage. Reproduce the browser checks using the table above and
the same actual app/settings; these are preliminary checks, not a participant
before/after experiment.

Execution constraints recorded: initial `git fetch` failed with read-only
`.git/FETCH_HEAD`; clone/pip/uv downloads failed DNS in the sandbox; API startup
reported `could not bind on any address ... ('127.0.0.1', 8000)`. Baseline and
integrated `timeout 20 ... pytest` attempts stalled and exited 124 without test
results. Retrying those operations with approved execution outside the sandbox
succeeded. An initial browser run captured the questions/votes but timed out on
an incorrect `Main menu` accessible-name selector; it was corrected to the actual
Streamlit menu test ID and the complete flow rerun. These are environment/harness
failures, not application acceptance passes.

## Existing complete-section study option

The team's existing `LLM_PROVIDER=template` mode uses retrieval without a model.
A separate actual API check returned `path=retrieval`, `degraded=false`, correct
IDs/titles and both complete source sections: the thesis credit/GPA rule, and
Student Affairs I.102 with 50,000 VND / three working days. See
[template-provider results](evidence/template-study-results.json). This is a
configuration option, not a production fix. It still quotes the thesis rule
rather than explicitly comparing 118 with 120. Record the selected provider
before the external session and capture a new study baseline. The screenshots
above remain labelled as stub-browser evidence.

## Preliminary findings — no participant observations

- The stub gives the correct thesis threshold/GPA and source, but does not
  explicitly conclude that 118 credits is insufficient. Evaluate whether an
  external user can make that inference unaided.
- The normal stub card answer gives Student Affairs I.102 and `S26#3`, but omits
  **50,000 VND / three working days**. The stub copies only the first sentence;
  fallback returns the whole section. Full observer answer-key completeness is
  therefore **not met** in the normal stub path.
- Submitting the full compound study task as one question produces only the
  card answer/source. This is an observed technical limitation, not proof that
  a participant will submit a compound question.
- At phone width the sidebar hides AI disclosure and the full example list;
  the welcome still supplies one example. Source text wraps and voting controls
  stack. The chat placeholder truncates. Inspect discoverability with the user.
- Source captions and the sidebar disclosure look faint. This is qualitative
  developer inspection; no measured WCAG contrast compliance is claimed.
- Backend-down banner includes a server-start command aimed at developers.
  A student-oriented recovery instruction is a possible UI improvement.

Owner/file/change candidates and the actual-observation requirement are recorded
once in [release evidence](release_evidence.md). No production fixes or claimed
participant outcomes are included here.
