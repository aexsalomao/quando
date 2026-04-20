---
name: calendar-method-add
description: Add a new public method to quando's calendar API with correct input auto-detection, exchange-calendar resolution, and parametrized tests across the full input-format matrix. Use when the user asks to add a method, new helper, new date operation, or extend the calendar surface.
---

# Add a Calendar Method

quando exposes 52 public methods across conversion, timezone, validation, day checks, navigation, ranges, period boundaries, settlement, and expiry. A new method must fit that surface cleanly and survive the auto-detecting input layer.

## Before writing code

Identify which module the method belongs in — one of:
- `_convert.py` — format conversions
- `_timezone.py` — timezone handling
- `_validate.py`, `_checks.py` — validation and day-type predicates
- `_navigate.py` — next/prev/add business days
- `_ranges.py` — date ranges
- `_periods.py` — month/quarter/year/week boundaries + rebalance triggers
- `_settlement.py` — T+N, COB roll-back, expiries
- `_parse.py` — input normalization (rare; only extend here if adding a new input *format*)

If the method doesn't fit one module, it's probably two methods.

## Input contract (non-negotiable)

Every public method accepts the same input types — enforce this via `_parse.py`:

- `str` in ISO (`2026-04-20`), compact (`20260420`), US (`04/20/2026`), or slash (`2026/04/20`) form
- `datetime.datetime`, `datetime.date`
- `int` / `float` as Unix epoch seconds **or** Excel West serial (context-dependent; document which)

If the method takes a date, it must auto-detect. If it takes multiple dates, all of them must auto-detect independently.

## Exchange calendar resolution

If the method depends on a trading calendar:
- Accept an optional `exchange: str | None = None` argument.
- Resolve via the active calendar when `None` (see `_state.py`).
- Never hardcode `"NYSE"` — users configure this.
- Custom holidays from the pluggable JSON loader must apply transparently.

## Tests (this is where most bugs live)

Put tests in `tests/test_<module>.py` mirroring `src/quando/_<module>.py`.

**Required test coverage for every new method:**

1. **Input-format matrix** — `@pytest.mark.parametrize` across all six input forms (ISO str, compact str, US str, slash str, `datetime`, `date`, `int` epoch). Parametrize ids so failures name the format.
2. **Happy path** — at least 3 cases for different inputs/expected outputs.
3. **Edge cases** — month/quarter/year boundaries, leap day (Feb 29), DST transition days (for any timezone-sensitive method), empty or single-day ranges.
4. **Holiday interaction** — at least one case using a known exchange holiday (e.g., NYSE 2026-01-01, 2026-07-03).
5. **Custom-holiday interaction** — load a JSON override in the test and assert the method respects it.
6. **Invalid input** — `pytest.raises(ValueError)` for malformed strings and unsupported types. Reference the fail-loud change in `quando 0.2.1` (malformed JSON raises, no silent fallback).
7. **No `time.sleep`, no network, no filesystem outside `tmp_path`** — project testing rule (§30–34).
8. **Loops forbidden in tests** — if you're tempted to loop, you want `@pytest.mark.parametrize` (rule §5).

## Checklist before marking the method done

- [ ] Type hints on all args and return value. Native types (`list[date]`, not `List[date]`).
- [ ] Docstring: one-line summary; multi-line only if behavior is non-trivial.
- [ ] Exported from `src/quando/__init__.py` (otherwise it's not public).
- [ ] Added to the README feature table or method count if that claim changes.
- [ ] `CHANGELOG.md` entry under `## [Unreleased]` → `### Added`.
- [ ] `uv run ruff check && uv run ruff format --check && uv run mypy --strict src && uv run pytest` all green.

## What not to do

- Don't add a `Union[str, date, datetime]` on individual methods — delegate to the parser. DRY the detection logic.
- Don't hardcode the exchange or today's date. Inject.
- Don't add a method that *only* wraps an `exchange-calendars` call with a rename. That's not value.
- Don't use `@pytest.mark.parametrize` as a substitute for separate tests of semantically different behaviors — parametrize *same behavior, different inputs* (rule §20).
