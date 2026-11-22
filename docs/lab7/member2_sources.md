# Lab 7 Member 2 source display

L1 formats the API source list as a caption below the answer. An empty list yields an empty string. A nonempty list uses one `Sources: ` prefix and preserves each source ID and title in API order, joined with `; `.

TV3 reviews the formatter. TV6 can use the dedicated L1 tests alongside the shared UI suite. TV1’s Streamlit app renders the caption and TV5’s HTTP client supplies the source list.

[Instructor starter](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/397639e11ac3bb47516d5de8211ccbfb3955794a/lab07/starter)

## Verification

Python 3.11.18 was used for the checks.

```powershell
python -m pytest -q tests/test_ui_sources.py -p no:cacheprovider
python -m ruff check ui/logic.py tests/test_ui_sources.py --no-cache
python -m pytest -q -p no:cacheprovider --tb=short
```

The three exact-output tests and Ruff passed. The full suite reported 155 passes and one failure. The existing Lab 5 migration test calls `len(saved.feedback)` on a single `Feedback` object. The same failure is recorded in the [Lab 6 comparison report](../lab6/path_comparison.md#verification).

### Streamlit caption check

Streamlit 1.39.0 AppTest ran the pinned instructor app and HTTP client in an ignored scratch copy with this branch’s `ui/logic.py`. The real client parsed synthetic `/v1/chat` JSON through HTTPX MockTransport, and the harness clicked three sidebar examples. It inspected the latest assistant chat block after each rerun and matched the exact captions below the answer.

| Synthetic response | Observed caption |
| --- | --- |
| One source | `Sources: H26#5.3 — 5.3 Thesis registration` |
| No sources | No caption element |
| Two sources | `Sources: S26#1 — 1 Library borrowing; H26#5.3 — 5.3 Thesis registration` |

All three scenarios passed in the starter app. TV6 can repeat the same cases after the team app and client land.
