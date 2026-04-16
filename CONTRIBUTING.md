# Contributing

Thanks for your interest in contributing to quando!

## Setup

```bash
git clone https://github.com/aexsalomao/quando
cd quando
uv sync --extra dev
pre-commit install
```

## Workflow

1. Fork the repo and create a branch: `{name}_fix_{description}` or `{name}_dev_{description}`
2. Make your changes
3. Run the full check suite locally before pushing:

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src/
uv run pytest
```

4. Open a pull request against `master`

CI runs the same checks automatically on every PR.

## Adding a Calendar

quando draws holiday data from `exchange-calendars`. To use any exchange it supports:

```python
q.use("XLON")   # London Stock Exchange via exchange-calendars code
```

To define a fully custom calendar with one-off closures:

```python
q.use("MY_FUND")
q.add_holiday("2024-07-05", "Fund closure day")
q.save_calendar("fund_calendar.json")
```

## Code Style

- Ruff for linting and formatting (enforced via pre-commit)
- mypy for static type checking — public functions should be annotated
- No lazy imports inside functions — all imports at module top (no circular deps exist)
- `_parse.py` and `_state.py` are the import roots; keep them free of local imports
- Pure functions preferred; `cal=None` always falls back to the global calendar
- No speculative abstractions — solve the problem at hand

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `_parse.py` | Universal input → UTC-aware `datetime`. No local imports. |
| `_state.py` | Global state: active calendar, verbosity, `as_of`. Imports `_parse` only. |
| `_calendar.py` | Holiday data: `exchange-calendars` + custom overrides + LRU cache. |
| `_checks.py` | Day classification: weekend, holiday, business day, expiry. |
| `_navigate.py` | Step-by-step business day walks. |
| `_ranges.py` | Date range generation and business day counting. |
| `_periods.py` | Period boundary computation + rebalancing checks. |
| `_settlement.py` | T+N settlement, COB roll, expiry dates. |

## Future contributions

Areas where help is especially welcome:

- Additional exchange calendars and timezone coverage
- `date_range()` returning a Polars/pandas Series
- `rebalance_schedule(start, end, freq)` convenience wrapper
- Session open/close times via `exchange-calendars`
- Async support for I/O operations
