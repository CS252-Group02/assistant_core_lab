# Lab 6 Member 6 path comparison

The Part F evaluation compares deterministic, retrieval-only, and stub LLM paths on E01–E20. The shared `eval/cases.jsonl` contains E01–E25 for Member 7's H1 evaluation.

Use the instructor's [Lab 6 starter](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/ea80fc97f747cadecde2262c9fd934eb2393c082/lab06) for the evaluator, baseline cases, and worksheet. Run the baseline in a separate directory containing the integrated code and knowledge base. The evaluator reads `eval/cases.jsonl` relative to its working directory.

Use the offline stub, BM25 with a minimum score of 2.0, prompt `answer_v1`, and the default tuition configuration. Record correctness, abstentions, latency, and failure IDs from the evaluator.
