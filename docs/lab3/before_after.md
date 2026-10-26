# Lab 3 — Before / after maintainability comparison

Fill in for the monolith (before) and your refactored package (after).

| Question | Before | After |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 constant in code (`RATE` in `assistant_monolith.py`) | 1 variable in `.env` (`CREDIT_RATE_VND`) |
| Can you run the tests without internet or an API key? | No (random timeout and failure in `llm()`) | Yes (deterministic offline unit tests) |
| What happens if `handbook.json` is missing? | Prints and continues silently | Raises `DataError` at startup fail-fast |
| Is any secret printed or logged? | Yes (`API_KEY` printed in debug output) | No (`repr=False` on `llm_api_key`) |
| How long does it take a new teammate to find the fee logic? | Needs to read through 160+ line monolithic `handle()` | Instantly located in `tools.py` |
| Number of global variables | 9 (3 mutable: `history`, `offices`, `handbook`) | 0 (pure functions & dependency injection) |
| Number of bare `except:` blocks | 3 (`load()`, `handle()`, `main()`) | 0 (specific exceptions, e.g. `DataError`, `InvalidRequest`) |
| Lines in the longest function | ~65 lines (`handle()`) | ~15 lines |
| `ruff check` issues | 11 errors (bare except, line length, multiple imports) | 0 errors (all checks passed) |
| Can you swap the LLM without touching the service? | No (tightly coupled inside monolith) | Yes (via `Responder` protocol / adapter pattern) |

**Three sentences:** What improved most is the decoupling of business logic and data access into pure, testable modules without global mutable state or hardcoded secrets. What got more complex is the introduction of multiple files, Pydantic data models, and dependency injection wiring. In the future, I would still add caching for handbook searches and support fuzzy matching for office names.
