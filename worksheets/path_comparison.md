# Lab 6 — Three assistant paths

Results from the original E01?E20 dataset. See [the run report](../docs/lab6/path_comparison.md) for reproduction.

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 7/20 | 5/5 | 0.0 ms | 5 | No document retrieval, so policy questions go unanswered. |
| retrieval | 16/20 | 4/5 | 0.1 ms | 4 | Keyword retrieval can quote a related section that does not answer the question. |
| llm (provider: stub) | 16/20 | 4/5 | 0.3 ms | 3 | The stub relies on the same top passage and inherits retrieval and routing errors. |

Which path would you ship for policy questions, and why? (3 sentences)

I would ship retrieval-only for policy questions because it matched the stub?s score of 16/20 and quoted the selected source directly. Keep the abstention and escalation behavior, and review the open-book exam case, where both paths returned an unrelated policy instead of abstaining. The stub results support an offline baseline and leave real model quality and latency open for a separate evaluation.
