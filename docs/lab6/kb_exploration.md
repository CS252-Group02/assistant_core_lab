# Knowledge base retrieval exploration

This is a local adaptation of Task 1 for the current checkout. The task image
refers to `data/kb/*.md` and an existing RAG BM25 index, but neither is present
here. This experiment uses all five rules from `data/handbook.json`, one rule
per chunk, with the rule ID and title as metadata. Indexed text combines the
title and body. It does not change the existing `Handbook.search` behavior or
service retrieval path.

## Method

Run `python scripts/explore_handbook_bm25.py` to reproduce the results. The
script lowercases text and tokenizes with `[a-z0-9]+`. It scores title and body
tokens with BM25 using `k1=1.5`, `b=0.75`, and positive IDF
`log(1 + (N - df + 0.5) / (df + 0.5))`. Results sort by descending score, then
chunk ID; zero-score chunks are omitted. No external indexing dependency is
required.

## Searches

| Query | Top chunk ID | Score |
| --- | --- | ---: |
| `can I register my thesis with 118 credits` | `H26-5.3` | 2.5897 |
| `policy on retaking a course` | `H26-4.2` | 3.2918 |
| `absence from final exam due to medical reasons` | `H26-7.2` | 9.1679 |

The first search also ranks `H26-5.4` (Late thesis registration) second, at
1.4071. That is a useful surprise: the query says the student has only 118
credits, yet the lexical ranker matches the shared “thesis registration” title.
BM25 does not reason about whether 118 meets the 120-credit requirement, so
the top match still needs to be checked against the rule text.

## Limits

These results describe a five-rule handbook experiment, not the missing Lab 6
KB corpus or another member's RAG implementation. The task image's three
original questions were not present in this checkout, so these searches reuse
the three rule-search examples in `tests/test_knowledge.py`.
