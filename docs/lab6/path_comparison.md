# Lab 6 Member 6 path comparison

The Part F evaluation compares deterministic, retrieval-only, and stub LLM paths on E01–E20. The shared `eval/cases.jsonl` contains E01–E25 for Member 7's H1 evaluation.

Use the instructor's [Lab 6 starter](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/ea80fc97f747cadecde2262c9fd934eb2393c082/lab06) for the evaluator, baseline cases, and worksheet. Run the baseline in a separate directory containing the integrated code and knowledge base. The evaluator reads `eval/cases.jsonl` relative to its working directory.

Use the offline stub, BM25 with a minimum score of 2.0, prompt `answer_v1`, and the default tuition configuration. Record correctness, abstentions, latency, and failure IDs from the evaluator.


## Measured results

The baseline ran on 2026-11-19 using team commit `b187cbf28d98a827db8cce23231b3e409e326b90` on Windows with Python 3.11.18. All paths used the integrated KB and the same original 20 cases, including five abstention cases.

```text
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     3.5   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.1     0.2   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.3    21.6   fails: E13 E14 E15 E19
```


The evaluator scores policy cases by the expected source ID, tool and lookup cases by the expected text, and abstention cases by an abstain path or unknown intent. These checks leave the full answer's meaning and completeness unscored. Latencies are rounded to one decimal place and vary by run. The stub runs locally, so its timing cannot predict live model latency.

Controllability ratings in the [completed worksheet](../../worksheets/path_comparison.md) reflect how directly the team can predict and audit each path. Deterministic scores 5 for its explicit routing and tools. Retrieval scores 4 because it quotes a traceable passage but depends on ranking and the threshold. The LLM path scores 3 because structured output and citation checks constrain it, while its generated text introduces another variable.

| Case | Observed failure |
| --- | --- |
| E13 | The tuition deadline question went to the fee calculator, which asked for the number of credits. |
| E14 | Retrieval selected the exam absence section `H26#7.2` for a question about credit load. |
| E15 | The office lookup gave the library location and hours for a borrowing period question. |
| E19 | Retrieval returned exam absence guidance for an open-book exam question that should have triggered abstention. |

## Reproduce

Run from the repository root in a fresh PowerShell session with the Python 3.11 lab environment active and dependencies installed. The copy uses a new ignored directory and places the 20 original cases where the evaluator expects them.

```powershell
$python = (Get-Command python).Source
$repo = (Get-Location).Path
$run = Join-Path $repo ('.lab5-tmp/lab06-f-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $run 'eval') -Force | Out-Null
Copy-Item src,data -Destination $run -Recurse
Copy-Item eval/compare_paths.py -Destination (Join-Path $run 'eval')
Copy-Item eval/cases_original20.jsonl -Destination (Join-Path $run 'eval/cases.jsonl')
Push-Location $run
try {
    $env:PYTHONPATH = Join-Path $run 'src'
    $env:ASSISTANT_DATA_DIR = 'data'
    $env:KB_DIR = 'data/kb'
    $env:LLM_PROVIDER = 'stub'
    $env:RETRIEVAL_KIND = 'bm25'
    $env:RETRIEVAL_MIN_SCORE = '2.0'
    $env:PROMPT_VERSION = 'answer_v1'
    $env:CREDIT_RATE_VND = '450000'
    $env:RETAKE_MULTIPLIER = '1.5'
    $env:MAX_CREDITS = '30'
    & $python eval/compare_paths.py
} finally {
    Pop-Location
}
```

## Verification

- The committed evaluator and original case fixture match the pinned instructor files byte for byte.
- The fixture contains E01?E20 in order, including five abstentions. The shared 25-case fixture and the H1 report match the team base.
- RAG tests passed **15/15**, and Ruff passed for the evaluator.
- The full suite reported **152 passed and 1 failed**. The pre-existing Lab 5 migration test expects a feedback collection, while the integrated ORM returns a single `Feedback` object. The [Member 2 grounding report](member2_grounding.md#existing-repository-regression-checks) records the same failure.
