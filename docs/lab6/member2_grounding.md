# Lab 6 — Member 2: Grounding A2

## Objective and ownership

Complete TODO A2 in `src/assistant_core/llm.py`, inside `parse_draft`.
A non-abstaining draft must cite at least one source, and every cited ID
must belong to the chunks retrieved for that request. Otherwise, raise
`ProviderError("answer cites sources that were not retrieved")`.

This document records Member 2's implementation scope and handoff. It is
not the team's grounding/fallback verification report.

## Supplied source and permitted changes

Use `D:/Lab_CT/public_materials/lab06/starter/` as the source. Map its
`src/` directory to this repository's `src/`, preserving filenames and
directory structure.

| Starter file | Repository destination | Planned change |
| --- | --- | --- |
| `src/assistant_core/llm.py` | `src/assistant_core/llm.py` | Copy unchanged first, then complete only TODO A2. |
| `src/assistant_core/prompts/answer_v1.txt` | `src/assistant_core/prompts/answer_v1.txt` | Copy unchanged. |

The only additional file owned by this task is
`docs/lab6/member2_grounding.md` for scope, validation evidence, and handoff.
Reuse the supplied JSON parser, `AnswerDraft`, providers, and prompt.

## Grounding contract

- Keep `parse_draft(raw: str, allowed_ids: set[str]) -> AnswerDraft` unchanged.
- Run citation validation after the existing JSON/schema validation succeeds.
- When `abstain` is false, reject an empty or omitted `source_ids` field,
  or any citation outside `allowed_ids`, using the error specified above.
- When `abstain` is true, skip the A2 citation check, as specified by the starter TODO.
- Preserve existing handling of malformed JSON and invalid schemas.
- Do not add answer-content verification or citation deduplication.

## Outside Member 2's scope

- A1 abstention and edits to `rag/answerer.py` belong to Member 3.
- Knowledge-base exploration, retrieval modules, and final integration belong
  to the members responsible for those components.
- Shared grounding tests, retry/fallback verification, and the team grounding
  verification report belong to Member 4; coordinate missing coverage with them.
- Do not change service/API integration, shared models, dependencies, evaluation
  cases, baseline comparisons, or existing Lab 5 behavior for this task.
- Do not copy the whole starter into the repository.

## Dependencies and validation plan

At the initial inspection, this repository contains Lab 5 code and does not
yet contain `llm.py`, the answer prompt, or the `rag` package.
The supplied `llm.py` imports `rag.index.Hit`, and `rag.index` imports
`rag.chunker.Chunk`. Those modules must come from the teammates responsible
for integrating them; their absence does not expand Member 2's file ownership.

After A2 is implemented, check `parse_draft` with synthetic JSON:

| Draft / citations | Expected outcome |
| --- | --- |
| Non-abstaining; one or multiple retrieved IDs | Return `AnswerDraft`. |
| Non-abstaining; empty or omitted citations | Raise `ProviderError`. |
| Non-abstaining; unknown ID | Raise `ProviderError`. |
| Non-abstaining; a mixture of retrieved and unknown IDs | Raise `ProviderError`. |
| Non-abstaining; empty `allowed_ids` | Raise `ProviderError`. |
| Abstaining; empty or unknown citations | Pass the A2 citation check. |
| Malformed JSON or invalid schema | Preserve the parser's `ProviderError`. |

While integration is pending, direct checks may use supplied dependencies in
an isolated temporary copy excluded from Git. Record these separately from
checks against the integrated repository. No real model or API key is needed.

Once Member 4's shared tests and their dependencies are available, run:

```powershell
python -m pytest -q tests/test_rag.py -k citation
```

Record the actual selected test count and result; zero selected tests is not
acceptance. Run existing tests for regression checks and report unrelated
failures to their owners instead of modifying their code.

## Five-commit sequence

1. `docs(lab6): define member 2 grounding scope` — add this scope and handoff plan.
2. `chore(lab6): add supplied LLM adapter` — copy `llm.py` unchanged, retaining TODO A2.
3. `chore(lab6): add supplied answer prompt` — copy `answer_v1.txt` unchanged.
4. `fix(lab6): enforce retrieved citation validation` — implement A2 and perform direct checks.
5. `docs(lab6): record A2 validation and handoff` — record actual results and the Member 4 handoff.

## Validation evidence — 2026-11-17

Implementation commit: `70db2d9` (`fix(lab6): enforce retrieved citation validation`).
Only the four-line TODO A2 comment was replaced with the required two-line
condition and `ProviderError`. Parsing, schemas, providers, and the prompt
remain as supplied. The prompt's SHA256 matches the starter:
`1FD0DCA95451F664487931A3FAA475FC9E840A31CBD4990FF4535D021CA903C8`.

Validation used `.venv-lab5/Scripts/python.exe` (Python 3.11.18,
pytest 8.3.3, Pydantic 2.9.2). The separate `.venv` does not contain pytest;
no dependencies were installed or changed.

### Direct A2 checks

An inline Python script, executed through `.venv-lab5/Scripts/python.exe -`,
copied the supplied starter to `.lab5-tmp/member2-a2/starter/` and replaced
only its `src/assistant_core/llm.py` with this repository's implementation.
The script imported `parse_draft` from that isolated copy and asserted outcomes
for synthetic JSON, including the exact grounding error message.
The existing `.gitignore` excludes `.lab5-tmp/`; no shared tests or retrieval
modules were added to the repository's tracked source.

| Check | Actual result |
| --- | --- |
| One retrieved citation | PASS: returns draft. |
| Multiple retrieved citations | PASS: returns draft. |
| Empty citations | PASS: raises the specified grounding error. |
| Omitted citations | PASS: raises the specified grounding error. |
| Unknown citation | PASS: raises the specified grounding error. |
| Mixed retrieved and unknown citations | PASS: raises the specified grounding error. |
| Empty allowed-ID set | PASS: raises the specified grounding error. |
| Abstaining with empty citations | PASS: returns draft. |
| Abstaining with an unknown citation | PASS: returns draft. |
| Confidence outside the schema range | PASS: preserves structured-output error. |
| Output with no JSON object | PASS: preserves no-JSON error. |
| Malformed JSON object | PASS: preserves structured-output error. |

Result: **12 direct checks passed**, without model or network calls.

### Supplied citation test in the isolated starter

From `.lab5-tmp/member2-a2/starter/`, using the absolute path to the
repository's `.venv-lab5/Scripts/python.exe`, run:

```powershell
python -m pytest -q -p no:cacheprovider tests/test_rag.py -k citation
```

Actual result: **1 passed, 14 deselected**. This executes the supplied
`test_citation_of_unretrieved_source_is_rejected` against the updated adapter.
This is an isolated starter check, not an integrated repository test result.

### Existing repository regression checks

From the repository root:

```powershell
.venv-lab5/Scripts/python.exe -m pytest -q -p no:cacheprovider --tb=short
.venv-lab5/Scripts/python.exe -m ruff check src/assistant_core/llm.py
git diff --check
```

- Regression: **137 passed, 1 failed**, with one dependency deprecation warning.
- The failure is `tests/lab5/test_scripts.py::test_migrations_are_repeatable_and_preserve_data`,
  line 63: `len(saved.feedback)` raises `TypeError: object of type 'Feedback' has no len()`.
- The same single test was run against an isolated `git archive` of the original
  commit `79d26ba`, under `.lab5-tmp/member2-baseline/repo/`. It fails with the
  same exception at the same assertion, confirming a pre-existing Lab 5 failure.
  No Lab 5 code or tests were changed.
- Ruff: **All checks passed**. Diff whitespace check: **passed**.
- Initial sandboxed regression attempts hit `PermissionError` accessing pytest
  temporary directories. The regression and baseline results above were obtained
  by rerunning outside that sandbox restriction, without changing test code.

## Handoff and remaining integration acceptance

The Member 2 implementation and five-commit sequence are complete. The final
tracked diff is limited to `llm.py`, the supplied answer prompt, and this document.

The repository still has no `src/assistant_core/rag/` package or
`tests/test_rag.py`. Running the required citation command in the repository
currently reports `file or directory not found: tests/test_rag.py`; it is not
an acceptance pass. Members responsible for integration must supply the retrieval
modules and shared tests, then rerun:

```powershell
python -m pytest -q tests/test_rag.py -k citation
```

Member 4 should use the direct-check matrix above to identify gaps in shared
coverage, and verify retry/fallback behavior using the supplied stubs. Member 2
does not modify retry/fallback or A1. Integrated citation acceptance remains
pending until the required command passes in the combined repository. The
pre-existing Lab 5 failure should be handed to its owner separately.
