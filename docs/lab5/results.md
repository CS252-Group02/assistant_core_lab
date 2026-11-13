# Lab 5 query results

All results come from a fresh synthetic database. No student data, raw messages,
session IDs, or real secrets are included. Queries are in `sql/my_queries.sql`.

- Base commit: `204cd47`
- Python: 3.14.9 (scratch venv; latest `sqlmodel`/`pydantic` because the pinned `pydantic-core` does not build on 3.14)
- Migrate: `python scripts/migrate.py assistant.db` (applies `001_init.sql`, `002_add_faq.sql`)
- Seed: `python scripts/seed.py assistant.db 300` (`random.seed(7)`, 300 interactions)

> Note: when these results were taken, R1 (`add_feedback`) was not merged yet, so
> feedback was inserted with the R1 code from the TODO hint. Re-run after R1 lands;
> the numbers should be the same because the seed is fixed.

## F1 - Requests per intent

| intent | requests |
| --- | --- |
| rule | 140 |
| fee | 61 |
| office | 47 |
| greeting | 26 |
| unknown | 26 |

`rule` is the most requested intent (140 of 300, about 47%). Students mostly ask
about handbook rules, so rule answers matter most for quality.

## F2 - Average latency per intent

| intent | avg_latency_ms |
| --- | --- |
| rule | 76.2 |
| fee | 5.1 |
| office | 3.4 |
| greeting | 2.4 |
| unknown | 8.1 |

`rule` is by far the slowest (76.2 ms), much slower than the other intents.
Rule answers do retrieval over the handbook, and degraded answers take about 4x longer,
so `rule` is the first place to optimise. Rows keep the F1 order (by request count).

## F3 - Topics receiving the most thumbs-down

| topic | thumbs_down |
| --- | --- |
| NULL | 17 |
| H26-4.2 | 8 |
| H26-5.3 | 8 |
| H26-7.2 | 2 |

The NULL group is the largest. Interactions with no handbook source (`unknown`,
`greeting`, `fee`, `office`) have a null topic, and every `unknown` answer is unresolved,
so it always receives thumbs-down. Among real rules, `H26-4.2` and `H26-5.3` each received
8 thumbs-down and are worth reviewing first. `H26-7.2` has only 2, but it is also asked
the least, so its rate is not small.

## H2 - Busiest UTC hours

| hour | requests |
| --- | --- |
| 16 | 300 |

All 300 interactions fall in UTC hour `16`, because the seed script stamps every row with
the time it ran (`utcnow()`), not a spread of times. The query is correct (it is
checked against fixed timestamps in `tests/lab5/test_sql.py`), but this synthetic data cannot
show a real daily pattern. The hour is UTC; in Vietnam (UTC+7) 16:00 UTC is 23:00 local.
