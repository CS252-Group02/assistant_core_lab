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
a temporary environment outside the repository. Record these separately from
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

## Current evidence and completion criteria

This first commit defines scope only. A2 is not implemented and no A2 test
results are claimed here.

Completion requires the supplied adapter and prompt, the A2 citation check,
passing integrated citation tests, and recorded commands/results. The final
Member 2 diff must remain limited to the two source files and this document.
