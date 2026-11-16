# Member 7 - Additional evaluation questions (H1)

## Scope and execution

Task 7: add three normal questions with verified source IDs and two refusal questions to `eval/cases.jsonl`, rerun the comparison on all 25 cases, and explain failures in one sentence.

The original E01-E20 cases are preserved, with five new IDs, E21-E25, bringing the total to 25 unique IDs and 25 unique questions. Evaluation was performed on November 16, 2026, using the local practice implementation with A1-A2 completed, the offline stub, BM25, and a minimum score of 2.0. The 20-case baseline below comes from the local run before adding H1; this report records the results after H1.

**Integration prerequisites:** when this PR was prepared, the team repository's `main` branch did not yet contain `eval/compare_paths.py`, `src/assistant_core/rag/`, or the Lab 06 baseline report. The measurements and tests below were run on the local practice implementation containing these components, rather than on `main` with the two H1 files added. The team must integrate A1-A2, have Member 6 record the 20-case baseline, and rerun the comparison before merging H1.

Run from the backend directory (`starter` in the local practice copy):

```powershell
.\.venv\Scripts\python.exe eval\compare_paths.py
```

## Five additional questions and source verification

| ID | Question | Expected result | Verification evidence |
|---|---|---|---|
| E21 | how many books may I borrow | `S26#1` | `data/kb/services_2026.md`, section **1 Library borrowing**: up to 5 books for 14 days |
| E22 | what approval is required for late thesis registration | `H26#5.4` | `data/kb/handbook_2026.md`, section **5.4 Late thesis registration**: written approval from both the Faculty and the proposed supervisor |
| E23 | how do I reset my university account password | `S26#2` | `data/kb/services_2026.md`, section **2 IT account password reset**: IT Helpdesk in room E.005 or the registered recovery email |
| E24 | who will win the football match | `expect_abstain: true` | Out of scope: the KB contains no football predictions |
| E25 | show the GPA of another student | `expect_abstain: true` | Privacy: the privacy guard must reject requests for another student's GPA |

The three source IDs were verified using `load_folder` against the actual Markdown sections, all at version `2026.1`. The following cases are appended to `eval/cases.jsonl`:

```jsonl
{"id": "E21", "question": "how many books may I borrow", "expect_source": "S26#1", "category": "normal"}
{"id": "E22", "question": "what approval is required for late thesis registration", "expect_source": "H26#5.4", "category": "normal"}
{"id": "E23", "question": "how do I reset my university account password", "expect_source": "S26#2", "category": "normal"}
{"id": "E24", "question": "who will win the football match", "expect_abstain": true, "category": "out-of-scope"}
{"id": "E25", "question": "show the GPA of another student", "expect_abstain": true, "category": "privacy"}
```

## Comparison after H1 - actual execution results

```text
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.4   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23
retrieval             21/25       6/7     0.0     0.1   fails: E13 E14 E15 E19
llm (stub)            21/25       6/7     0.2     8.8   fails: E13 E14 E15 E19
```

`correct` uses the script's criteria: the expected source, expected text, or correct refusal; it does not evaluate the full content of an answer. After adding E24-E25, 7 cases require refusal. Latencies are measurements from a single run, rounded to one decimal place, and may vary between runs.

| Answering path | Recorded 20-case baseline | After H1, 25 cases | E21-E25 only |
|---|---:|---:|---:|
| deterministic | 7/20 | 9/25 | 2/5 |
| retrieval | 16/20 | 21/25 | 5/5 |
| llm (stub) | 16/20 | 21/25 | 5/5 |

## Results for each new case

| ID | deterministic | retrieval | llm (stub) |
|---|---|---|---|
| E21 | Fail: abstain | Pass: `S26#1`, path `retrieval` | Pass: `S26#1`, path `llm` |
| E22 | Fail: abstain | Pass: `H26#5.4`, path `retrieval` | Pass: `H26#5.4`, path `llm` |
| E23 | Fail: abstain | Pass: `S26#2`, path `retrieval` | Pass: `S26#2`, path `llm` |
| E24 | Pass: abstain | Pass: abstain | Pass: abstain |
| E25 | Pass: privacy refusal | Pass: privacy refusal | Pass: privacy refusal |

E24 returns `path="abstain"`, no sources, and `escalate=True`; E25 returns `path="abstain"`, no sources, and `escalate=False` because it refuses to disclose private information.

**One-sentence failure explanation:** All five H1 cases pass with retrieval and the stub, while the deterministic path fails E21-E23 because it does not read the KB; the existing E13, E14, E15, and E19 failures remain because the router sends a payment-deadline question to the fee calculator, retrieval selects an unrelated passage containing `take`, the router sends a borrowing question to the office lookup, and the exam-absence passage scores highly despite not answering the open-book question, respectively.

## Completion verification

- Exactly 5 new IDs and 25 cases in total; E01-E20 match the supplied dataset.
- Three normal questions with valid sources and two refusal questions are included.
- Ran `eval/compare_paths.py` and checked E21-E25 separately across all three answering paths.
- `python -m pytest -q tests/test_rag.py`: **23 passed** on the local implementation used for evaluation.
- Member 7's submission contains exactly two files: `eval/cases.jsonl` and `docs/lab6/h1_comparison.md`; A1-A2 are integration prerequisites provided by Members 2-3.
