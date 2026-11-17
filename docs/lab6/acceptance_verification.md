# Lab 06 — Member 5 (E): abstention and regression verification

**Status: verification implemented; integrated acceptance remains blocked.** All 12 new
checks pass on the existing A1 feature base. The complete regression suite has 12
failures, reproduced with the new test file excluded. No production fixes or teammate
branch merges were made to change those results.

## Plan and working base

1. Inspect Git state and current PRs; preserve local changes and select the existing Lab 6/A1 base.
2. Compare the instructor starter and existing tests; identify only missing Member 5 checks.
3. Add deterministic edge tests using the original interfaces and offline spies/stubs.
4. Run the required tests, evaluation entry point, and CLI examples; record actual results.
5. Review the two-file change, commit it, and hand off a draft PR with integration dependencies.

Verification date: **2026-11-17**, Asia/Ho_Chi_Minh (UTC+07:00).
The initial tree was clean on `feat/lab06-absention-verfication` at
`79d26bab9ecae078c0ff13f003d3c5432e5691f9`. That existing branch was preserved.
Remote refs were refreshed with `git fetch origin`.

Working branch: `feat/lab6-e-abstention-verification`.
Base: `origin/feat/lab6-a1-abstention`, commit
`253be41ad04495ee02eb333a5b6b896eed7e5e0b`.
It contains the starter integration and A1 implementation. `main` still has no Lab 6
RAG modules, so it was unsuitable for these acceptance tests.

| PR | Observed status | Head / target | Consequence |
| --- | --- | --- | --- |
| [#31](https://github.com/CS252-Group02/assistant_core_lab/pull/31) | Open, unmerged | `2badf0f` / `main` | Starter integration is available in the selected base. |
| [#33](https://github.com/CS252-Group02/assistant_core_lab/pull/33) | Open, unmerged | `253be41` / `feat/BaroTaro-lab06/add-test-and-intergration` | Selected existing A1 base; no A1 implementation copied or recreated. |
| [#34](https://github.com/CS252-Group02/assistant_core_lab/pull/34) | Open, unmerged | `d45b789` / `main` | A2 grounding validation is absent from the selected base. |
| [#28](https://github.com/CS252-Group02/assistant_core_lab/pull/28) | Open, unmerged | `ea4a88c` / `main` | H1 cases and report are not integrated here. |

The A1 base also predates `4a5f3b3`, `050402e`, and `79d26ba` on `main`.
In particular, `src/assistant_api/main.py` still uses the in-memory feedback store
instead of the Lab 5 persistence wiring. No branch was merged or cherry-picked.
The draft handoff should target `feat/lab6-a1-abstention`, the tested base, until
the integration owner reconciles the dependencies.

## Environment and offline execution

No project virtual environment was present, and `/usr/bin/python3` was Python 3.14.4
without the required packages. An isolated environment was prepared under `/tmp`
using Python 3.11, as documented by the repository. No dependency files changed.

| Component | Actual version |
| --- | --- |
| Python / executable | 3.11.18 / `/tmp/lab6-e-venv/bin/python` |
| Platform | Linux x86_64, glibc 2.43 |
| SQLite | 3.53.1 |
| pytest / ruff | 8.3.3 / 0.6.9 |
| pydantic / pydantic-core | 2.9.2 / 2.23.4 |
| python-dotenv | 1.0.1 |
| FastAPI / Starlette | 0.115.14 / 0.46.2 |
| httpx / uvicorn | 0.28.1 / 0.30.6 |
| SQLModel / SQLAlchemy | 0.0.22 / 2.0.58 |
| AnyIO | 4.16.0 |

Environment preparation used `uv 0.13.9` from a temporary bootstrap environment:

```bash
/tmp/lab6-e-bootstrap/bin/uv python install 3.11 --install-dir /tmp/lab6-e-python --cache-dir /tmp/lab6-e-uv-cache --no-bin
/tmp/lab6-e-bootstrap/bin/uv venv /tmp/lab6-e-venv --python /tmp/lab6-e-python/cpython-3.11.18-linux-x86_64-gnu/bin/python3.11 --cache-dir /tmp/lab6-e-uv-cache
/tmp/lab6-e-bootstrap/bin/uv pip install --python /tmp/lab6-e-venv/bin/python --cache-dir /tmp/lab6-e-uv-cache -r requirements.txt -e .
source /tmp/lab6-e-venv/bin/activate
export LLM_PROVIDER=stub LLM_API_KEY='' PYTHONHASHSEED=0
```

Network access was used only to inspect repositories and prepare the environment.
Verification used local knowledge files, `StubLLM`, fake indexes, mocked weather
transports, in-process API clients, and local SQLite databases. No real LLM, API
credentials, or external service was used for testing.

The first sandboxed full-suite attempt stalled in `TestClient.__enter__` and was
interrupted (exit 130). A diagnostic
`timeout 40s python -m pytest -vv -o faulthandler_timeout=15` collected 165 tests,
then showed the AnyIO thread portal waiting during the first API fixture; it
ended with exit 124. The complete full-suite and existing-test baseline results
below came from approved execution outside the sandbox, with the same offline
dependencies. The focused RAG and Member 5 runs completed inside the sandbox.

## Instructor comparison and reused coverage

All requested files were read from
[`public_materials/lab06/starter/`](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/ea80fc97f747cadecde2262c9fd934eb2393c082/lab06/starter).
The instructor's observed `main` commit was `ea80fc97f747cadecde2262c9fd934eb2393c082`.
Temporary comparison copies were stored under `/tmp/lab6-e-reference`; no tests
were executed against that reference copy.

Paths below are relative to `lab06/starter/` in the instructor repository and to
the root in the team repository.

| Reference file | Comparison with selected team base / reuse |
| --- | --- |
| `tests/test_rag.py` | Byte-identical; preserved all 15 collected cases. Blob `6203c8f11ea7d78140c84dfdb90051ecf45ee1a7`. |
| `src/assistant_core/rag/answerer.py` | Instructor implementation with the existing A1 change: `not hits or hits[0].score < self.min_score`. Reused directly. |
| `src/assistant_core/rag/index.py` | Byte-identical; reused `Hit`, `Index`, and `make_index`. |
| `src/assistant_core/rag/chunker.py` | Byte-identical; reused `Chunk` and `load_folder`. |
| `src/assistant_core/guard.py` | Byte-identical; reused the privacy examples and `PRIVATE_REPLY`. |
| `src/assistant_core/llm.py` | Byte-identical starter, including unresolved A2 TODO; reused `StubLLM`. |
| `src/assistant_core/tools.py` | Team retains existing formatting, exports, and case-insensitive parsing; instructor tool-call handling is present. Reused existing calculation and validation. |
| `src/assistant_core/service.py` | Same RAG/service interfaces; team retains its logger name and safe missing-office handling. Reused `AssistantService` and `build_service`. |
| `src/assistant_core/models.py` | Same public fields and defaults; docstrings/comments differ. Reused `Message`, `Response`, and `Intent`. |
| `src/assistant_core/config.py` | Same Lab 6 settings; team retains Lab 5 salt default and field ordering. Reused explicit `Settings`. |
| `eval/cases.jsonl` | Read the supplied 20 cases; absent from selected base. No copy added to this branch. |
| `eval/compare_paths.py` | Read the supplied comparison; absent from selected base. No copy added to this branch. |

No instructor production component was newly copied into the team tree by this task.

| Existing coverage reused | Missing coverage added in `tests/test_abstention_edges.py` |
| --- | --- |
| Chunk metadata; BM25/TF-IDF/hybrid thesis retrieval | Controlled scores independent of BM25 |
| Out-of-scope abstention checks path/escalation | Full no-hit response contract and proof of no LLM call |
| Grounded student-card answer (`S26#3`) | Successful password-reset answer (`S26#2`); card case retained in original suite |
| Invalid output fallback; provider failure fallback | No duplicate grounding/fallback tests added |
| Valid/invalid tool calls and tool execution | Fee handling bypasses both retrieval and LLM while RAG is enabled |
| Standalone privacy guard and own-question allowance | Service-level refusal and both dependency call counts for all three examples |
| Existing fee parsing, missing/zero/excessive credits, configured rates | Negative retake validation, previously uncovered |

## New edge results and call evidence

The new file collects **12 tests**, all passing. `FixedIndex.search(query, k=3)`
returns predetermined original `Hit` objects containing a real `S26#3` chunk.
`min_score` is explicitly `2.0`; no ranking score is inferred from BM25.

| Scenario | Actual result | LLM `complete()` calls |
| --- | --- | --- |
| No hits, with instrumented LLM | `abstain`, unknown, escalate true, confidence 0.0, sources `[]` | 0 |
| No hits, `llm=None` | Same abstention contract | No LLM configured |
| Top score 1.999, with instrumented LLM | Same abstention contract | 0 |
| Top score 1.999, `llm=None` | Same abstention contract | No LLM configured |
| Top score 2.0 | `llm`, rule, `S26#3`, no degradation/escalation | Exactly 1 |
| Top score 2.001 | `llm`, rule, `S26#3`, no degradation/escalation | Exactly 1 |
| `reset my password` | `llm`, rule, `S26#2`, nonempty answer, no degradation/escalation | Offline `StubLLM` |
| Each of the three supplied privacy requests | Exact `PRIVATE_REPLY`, `abstain`, unknown, escalate false, sources `[]` | 0; retrieval also 0 |
| `tuition for 18 credits and 2 retake` | `Your tuition is 9,450,000 VND.`, deterministic, fee | 0; retrieval also 0 |
| Direct tuition call with retake `-1` | `InvalidRequest`: `Retake credits cannot be negative.` | No LLM involved |

The no-call evidence is executable: the forbidden LLM's `complete()` raises
`AssertionError` if reached, and passing tests explicitly assert
`complete.assert_not_called()`. Privacy/fee tests install a forbidden index whose
`search()` also raises, then assert `search.assert_not_called()`. Privacy responses
equal the fixed refusal and contain no student ID or sources. Accepted boundary
tests wrap the original `StubLLM`, which returns structured JSON citing the retrieved
chunk, and assert `complete.assert_called_once()`. These passing assertions establish
call behavior; CLI output alone does not.

## Executed commands and results

Commands were run from the team repository, in the order shown for the first five rows.
All are against the incomplete A1 feature base plus the new tests, **not a fully
integrated team branch**. No test was deleted, weakened, skipped, or marked xfail.

| Exact command | Exit | Actual terminal summary |
| --- | --- | --- |
| `python -m pytest -q tests/test_rag.py` | 1 | `1 failed, 14 passed in 0.75s` |
| `python -m pytest -q tests/test_abstention_edges.py` | 0 | `12 passed in 0.34s` |
| `python -m pytest -q tests/test_rag.py tests/test_abstention_edges.py` | 1 | `1 failed, 26 passed in 0.54s` |
| `python -m pytest -q --collect-only tests/test_rag.py tests/test_abstention_edges.py` | 0 | `27 tests collected in 0.41s` |
| `python -m pytest -q` | 1 | `12 failed, 153 passed, 1 warning in 8.42s` |
| `python eval/compare_paths.py` | 2 | Missing script; output below. |
| `/tmp/lab6-e-venv/bin/python -m pytest -q --ignore=tests/test_abstention_edges.py` | 1 | `12 failed, 141 passed, 1 warning in 14.82s` |
| `python -m ruff check tests/test_abstention_edges.py` | 0 | `All checks passed!` |

The last pytest run is an additional baseline diagnostic of the unchanged existing
suite. It reproduces the same 12 failures with the new file excluded; the required
full run above included every configured test, including `practice/`.
The warning is Starlette's deprecated `anyio.abc.BlockingPortal` alias.

```text
python: can't open file '/home/zzzdarc/Lab_CT/assistant_core_lab/eval/compare_paths.py': [Errno 2] No such file or directory
```

No comparison score is reported because the team comparison could not run. H1's
PR report and temporary instructor files are not substitutes for that execution.

### All full-suite failures and handoff owners

| Failed node | Observed failure | Likely owner / dependency |
| --- | --- | --- |
| `tests/test_rag.py::test_citation_of_unretrieved_source_is_rejected` | `DID NOT RAISE ProviderError` | A2 owner, PR #34; grounding/fallback coordination with Member 4. |
| `tests/lab5/test_api_persistence.py::test_chat_records_metadata` | `NoResultFound` | Integration owner: bring existing Lab 5 API persistence into the Lab 6 base. |
| `tests/lab5/test_api_persistence.py::test_unknown_chat_is_unresolved` | `NoResultFound` | Same Lab 5 integration dependency. |
| `tests/lab5/test_api_persistence.py::test_rule_topic_matches_first_source` | `NoResultFound` | Same Lab 5 integration dependency. |
| `tests/lab5/test_api_persistence.py::test_degraded_response_is_recorded` | `NoResultFound` | Same Lab 5 integration dependency. |
| `tests/lab5/test_api_persistence.py::test_feedback_limit_reaches_repository` | Empty list instead of one feedback row | Same Lab 5 integration dependency. |
| `tests/lab5/test_api_persistence.py::test_unknown_feedback_returns_error_envelope` | 201 instead of 404 | Same Lab 5 integration dependency. |
| `tests/lab5/test_api_persistence.py::test_admin_endpoints_require_key` | `/v1/stats/intents` returns 404 instead of 401 | Same Lab 5 integration dependency. |
| `tests/lab5/test_api_persistence.py::test_stats_and_feedback_use_injected_repository` | Stats endpoint returns 404 instead of 200 | Same Lab 5 integration dependency. |
| `tests/lab5/test_api_persistence.py::test_feedback_survives_new_app_and_engine` | Empty feedback list after restart | Same Lab 5 integration dependency. |
| `tests/lab5/test_api_persistence.py::test_default_app_uses_database_settings` | Configured database file not created | Same Lab 5 integration dependency. |
| `tests/lab5/test_scripts.py::test_migrations_are_repeatable_and_preserve_data` | `len(saved.feedback)` raises `TypeError: object of type 'Feedback' has no len()` | Lab 5 repository/ORM owner: inspect relationship cardinality and dependency compatibility. |

`src/assistant_api/db.py` is unchanged from both the selected base and current
`origin/main`; the ORM failure is reproduced in the existing-only run. It has not
been diagnosed as an A1/A2 failure, and no full-suite run against `main` is claimed.
The original valid grounded answer, invalid-output fallback, provider-failure
fallback, tool-call tests, and standalone privacy tests all passed in the RAG run.

## Actual CLI evidence

With the environment above and `export LOG_LEVEL=ERROR` to suppress routine logs,
the following commands were executed as separate CLI subprocesses. Every command
returned exit 0, but only the fee example meets the intended Lab 6 behavior.

```text
$ python -m assistant_core "what is the capital of France"
Sorry, I don't know that yet.
$ python -m assistant_core "I lost my student card"
Retaking a course: Students may retake a course they failed. Retake credits are charged at 1.5 times the normal rate. Final-year students must register retakes before week 2.
$ python -m assistant_core "what grade did my friend get"
Sorry, I don't know that yet.
$ python -m assistant_core "tuition for 18 credits and 2 retake"
Your tuition is 9,450,000 VND.
```

The CLI only prints answer text. A separate observation run invoked its unchanged
`main()` and wrapped `AssistantService.handle` with `unittest.mock.patch.object`:
the wrapper called the original method, saved its returned `Response`, and returned
that same object. It confirmed these actual CLI response fields:

| Question | `path` | `intent` | `escalate` | `confidence` | Source IDs |
| --- | --- | --- | --- | --- | --- |
| Capital of France | deterministic | unknown | false | null | `[]` |
| Lost student card | deterministic | rule | false | null | `H26-4.2` |
| Friend's grade | deterministic | unknown | false | null | `[]` |
| 18 credits, 2 retake | deterministic | fee | false | null | `[]` |

All four had `degraded=false`. `__main__.py` constructs `AssistantService` without
a `rag` argument; it does not use `build_service()`. This explains the wrong card
answer, absent abstention path/escalation, and generic privacy answer. CLI wiring
belongs to integration and was left unchanged.

### Actual Lab 6 service response fields

For comparison, this terminal snippet exercised the existing Lab 6 factory on the
same team branch. This is service evidence, separate from the CLI results above.

```bash
python - <<'PY'
from assistant_core.config import Settings
from assistant_core.models import Message
from assistant_core.service import build_service
svc = build_service(Settings(llm_provider='stub', retrieval_kind='bm25', retrieval_min_score=2.0))
for question in [
    'what is the capital of France',
    'I lost my student card',
    'reset my password',
    'what grade did my friend get',
    'show the GPA of another student',
    'phone of 22127001',
    'tuition for 18 credits and 2 retake',
]:
    print(question)
    print(svc.handle(Message(text=question)).model_dump_json())
PY
```

Actual output:

```text
what is the capital of France
{"answer":"I'm not confident I can answer that from the official documents. Please contact the Training Office (room I.101) or ask your academic advisor.","intent":"unknown","sources":[],"degraded":false,"escalate":true,"path":"abstain","confidence":0.0}
I lost my student card
{"answer":"According to 3 Student card replacement: A lost student card can be replaced at Student Affairs (room I.102).","intent":"rule","sources":[{"id":"S26#3","title":"3 Student card replacement"}],"degraded":false,"escalate":false,"path":"llm","confidence":0.7}
reset my password
{"answer":"According to 2 IT account password reset: Students can reset their university account password at the IT Helpdesk (room E.005) or online with their registered recovery email.","intent":"rule","sources":[{"id":"S26#2","title":"2 IT account password reset"}],"degraded":false,"escalate":false,"path":"llm","confidence":0.7}
what grade did my friend get
{"answer":"I can't share information about other students. You can only see your own records after logging in.","intent":"unknown","sources":[],"degraded":false,"escalate":false,"path":"abstain","confidence":null}
show the GPA of another student
{"answer":"I can't share information about other students. You can only see your own records after logging in.","intent":"unknown","sources":[],"degraded":false,"escalate":false,"path":"abstain","confidence":null}
phone of 22127001
{"answer":"I can't share information about other students. You can only see your own records after logging in.","intent":"unknown","sources":[],"degraded":false,"escalate":false,"path":"abstain","confidence":null}
tuition for 18 credits and 2 retake
{"answer":"Your tuition is 9,450,000 VND.","intent":"fee","sources":[],"degraded":false,"escalate":false,"path":"deterministic","confidence":null}
```

## Scope and quality review

`git diff --check` and `git diff --cached --check` returned exit 0 with no output.
The staged diff was reviewed and contains only the two additions named below.
`git diff --stat HEAD` confirmed the same scope. A comparison against the A1 base
showed no changes to `src/`, the original RAG/service/tool tests, dependency files,
or root README. No new project dependency or testing framework was introduced.

## Acceptance handoff

Member 5's changes are limited to `tests/test_abstention_edges.py` and this report.
The original tests and production modules, shared evaluation files, dependency
files, and root documentation are unchanged. The new tests use pytest and Python's
standard-library mocks with the instructor's public interfaces.

Before Member 5 can be considered fully complete, the team must:

1. Reconcile the integration/A1 base with the existing Lab 5 API persistence work on `main`.
2. Integrate the existing A2 validation (PR #34), coordinating its regression result with the grounding/fallback owner.
3. Resolve the Lab 5 ORM relationship failure in the supported environment.
4. Wire the CLI to the Lab 6 service factory and rerun the four actual CLI examples.
5. Integrate the shared comparison script and evaluation cases through their owners, including pending H1 work as appropriate.
6. Rerun both focused suites, collection, the full regression suite, and the offline comparison on the fully integrated branch; replace this provisional status with those actual results.

This report and the draft PR provide the failure handoff for the A1/A2 and integration
owners. No claim of fully integrated acceptance or successful evaluation is made.
