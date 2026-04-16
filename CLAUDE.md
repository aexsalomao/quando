# quando

Time translation & holiday tracking for backtesting pipelines.

- **Python:** 3.10+ | **Build:** uv_build | **License:** MIT
- **Core deps:** `exchange-calendars>=4.0`
- **Dev deps:** `pytest>=8.0`, `pytest-cov`, `ruff`, `mypy`, `pre-commit`, `mkdocs`, `mkdocs-material`

## Setup & Tests

```bash
uv sync --extra dev
uv run pytest
uv run pytest --cov=quando  # with coverage
uv run ruff check .
uv run mypy src/
```

## Usage

```python
import quando as q

q.use("NYSE")                              # set global calendar (default: NYSE)
q.next_business_day("2024-12-24")
q.date_range("2024-01-01", "2024-03-31")
q.end_of_month("2024-01-15")
q.is_month_end("2024-01-31")              # True — rebalancing trigger
```

## Project Layout

```
src/quando/
    __init__.py        # all public exports + today()
    _parse.py          # parse() — any input → UTC-aware datetime
    _state.py          # global state: use(), verbose(), as_of(), get_cal/tz/xcal_name
    _calendar.py       # holiday data: exchange_calendars + custom overrides
    _checks.py         # is_weekend/holiday/business_day/expiry_day, day_of_week
    _convert.py        # to_timestamp/datetime/west/iso, convert(), batch ops
    _timezone.py       # shift_tz(), localize(), strip_tz()
    _validate.py       # is_valid(), is_same_day/before/after()
    _navigate.py       # next/prev_business_day, add_business_days, snap()
    _ranges.py         # business_days_between, date_range, trading_days_in_month/year
    _periods.py        # start/end of month/quarter/year/week + is_month/quarter/year_end
    _settlement.py     # to_settlement_date, to_cob, next_expiry, days_to_expiry
    _io.py             # load_calendar(), save_calendar()
tests/
    conftest.py        # autouse fixture: resets all global state between tests
    test_*.py          # one module per source file
```

## Import Graph

All imports are top-level (no lazy imports inside functions).

```
_parse.py         (stdlib only)
_state.py         → _parse
_calendar.py      → _parse, _state
_checks.py        → _parse, _state, _calendar
_convert.py       → _parse
_timezone.py      → _parse, pytz
_validate.py      → _parse
_navigate.py      → _parse, _checks
_ranges.py        → _parse, _checks
_periods.py       → _parse, _checks, _navigate
_settlement.py    → _parse, _checks, _navigate, _ranges
_io.py            → _state, _calendar
```

Note: `exchange_calendars` and `pandas` are imported lazily inside `_xcal_holidays()` only — they're heavy and wrapped in try/except for graceful failure.

## Conventions

- All inputs are auto-detected: `str`, `datetime`, `date`, `int`/`float` (Unix epoch or Excel West serial)
- `cal=None` falls back to the global calendar set by `q.use()`; default is `NYSE`
- All returned datetimes are UTC-aware unless a timezone is explicitly attached via `shift_tz`/`localize`
- "West" format = Excel serial integer (days since 1899-12-30, e.g. `45306` = 2024-01-15)
- `_WEST_EPOCH` is defined once in `_parse.py` and imported by `_convert.py`

## Module APIs

### `_state.py`

```python
use(cal: str)               # set global calendar ("NYSE", "LSE", etc.)
verbose(flag: bool)         # toggle debug logging
as_of(value)                # set reference date for expiry/settlement
get_cal(cal=None) -> str    # resolve cal or return global
get_tz(cal=None) -> str     # timezone name for cal (e.g. "America/New_York")
get_xcal_name(cal=None) -> str  # exchange-calendars code (e.g. "XNYS")
get_as_of() -> datetime | None
log(msg: str)               # logs if verbose=True

CAL_ALIAS: dict[str, str]   # "NYSE" → "XNYS", etc.
CAL_TZ: dict[str, str]      # "NYSE" → "America/New_York", etc.
```

### `_parse.py`

```python
_WEST_EPOCH = date(1899, 12, 30)
_WEST_MIN = 25569   # 1970-01-01
_WEST_MAX = 73050   # 2099-12-31

parse(value) -> datetime    # any input → UTC-aware datetime
```

Detection order: `datetime` → `date` → West serial int → Unix int/float → str (8 formats + dateutil fallback)

### `_calendar.py`

```python
_CUSTOM_ADD: dict     # {cal_name: {date: name}}
_CUSTOM_REMOVE: dict  # {cal_name: set[date]}

_xcal_holidays(xcal_name, year) -> tuple   # LRU-cached; clears on add/remove
get_holidays_for_year(cal_name, year) -> dict  # base + custom overrides
is_holiday_date(d: date, cal_name: str) -> bool

# public
list_holidays(year, cal=None) -> list[tuple[date, str]]
add_holiday(value, name, cal=None)
remove_holiday(value, cal=None)
```

### `_checks.py`

```python
is_weekend(value) -> bool
is_holiday(value, cal=None) -> bool       # weekday AND in holiday set
is_business_day(value, cal=None) -> bool  # not weekend AND not holiday
is_expiry_day(value) -> bool              # third Friday of month
day_of_week(value) -> str                 # "Monday" … "Sunday"
```

### `_navigate.py`

```python
next_business_day(value, cal=None) -> datetime
prev_business_day(value, cal=None) -> datetime
add_business_days(value, n: int, cal=None) -> datetime   # negative n goes backward
snap(value, direction: str, cal=None) -> datetime        # "forward"|"backward"|"nearest"
```

### `_ranges.py`

```python
business_days_between(start, end, cal=None) -> int   # exclusive of both endpoints
date_range(start, end, cal=None) -> list[datetime]   # business days, inclusive
trading_days_in_month(value, cal=None) -> int
trading_days_in_year(year: int, cal=None) -> int     # annualization factor (~252 NYSE)
filter_business_days(values, cal=None) -> list
```

### `_periods.py`

All functions return a UTC-aware `datetime` on a business day.

```python
# Month
start_of_month(value, cal=None) -> datetime    # first business day of month
end_of_month(value, cal=None) -> datetime      # last business day of month
is_month_end(value, cal=None) -> bool          # True if value IS end_of_month

# Quarter  (Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec)
start_of_quarter(value, cal=None) -> datetime
end_of_quarter(value, cal=None) -> datetime
is_quarter_end(value, cal=None) -> bool

# Year
start_of_year(value, cal=None) -> datetime
end_of_year(value, cal=None) -> datetime
is_year_end(value, cal=None) -> bool

# Week  (ISO week: Mon–Fri)
start_of_week(value, cal=None) -> datetime     # first business day of ISO week
end_of_week(value, cal=None) -> datetime       # last business day of ISO week
```

Rebalancing pattern:
```python
if q.is_month_end(today, cal="NYSE"):
    rebalance()
```

### `_settlement.py`

```python
to_settlement_date(value, convention: str, cal=None) -> datetime  # e.g. "T+2"
to_cob(value, cal=None) -> datetime     # rolls back if non-business day
next_expiry(value, contract_type: str) -> datetime  # "monthly"|"quarterly"|"weekly"
days_to_expiry(value, expiry, cal=None) -> int       # business days to expiry
```

### `_io.py`

```python
load_calendar(path: str)          # load JSON, sets active calendar
save_calendar(path: str, cal=None)  # export custom additions only (not exchange holidays)
```

JSON schema:
```json
{
  "name": "MY_CAL",
  "holidays": [
    {"date": "2024-07-04", "name": "Independence Day"}
  ]
}
```

## Supported Calendars

Built-in aliases: `NYSE`, `EUREX`, `LSE`, `TSX`, `ASX`, `HKEX`, `JPX`, `CME`

Any `exchange-calendars` exchange code also works (e.g. `"XLON"`, `"XEUR"`).

## Code Style

- **No lazy imports inside functions** — all imports at module top (no circular deps exist)
- **All public functions accept `cal=None`** — falls back to global; pass explicitly to override
- `_parse.py` and `_state.py` are the two roots of the import graph; keep them free of local imports
- `exchange_calendars`/`pandas` stay lazy inside `_xcal_holidays` — they're heavy and optional at import time
- Tests reset all global state via `conftest.py` autouse fixture
- Test anchors use 2024 NYSE calendar (verified holidays)
