# quando

> Navigate trading calendars, business days, and market periods — with zero fuss.

[![PyPI](https://img.shields.io/pypi/v/quando?color=blue)](https://pypi.org/project/quando/)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![CI](https://github.com/aexsalomao/quando/actions/workflows/ci.yml/badge.svg)](https://github.com/aexsalomao/quando/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-aexsalomao.github.io%2Fquando-blue)](https://aexsalomao.github.io/quando)

**quando** is a lightweight library for business day arithmetic and market calendar utilities. It auto-detects any date input, resolves holidays via [exchange-calendars](https://github.com/ryanking13/exchange-calendars), and provides 52 methods covering everything from date conversion to settlement dates and rebalancing triggers.

---

## Features

- **52 methods** — conversion, timezone, validation, day checks, navigation, ranges, period boundaries, settlement, and expiry
- **Auto-detecting inputs** — string (ISO, compact, US, slash), `datetime`, `date`, `int`/`float` (Unix epoch or Excel West serial)
- **Exchange calendars** — NYSE, EUREX, LSE, TSX, ASX, HKEX, JPX, CME via `exchange-calendars`; any exchange code works
- **Custom holidays** — add, remove, and persist overrides to JSON; merged transparently at query time
- **Period boundaries** — month, quarter, year, and ISO week; always snaps to the nearest business day
- **Rebalancing triggers** — `is_month_end()`, `is_quarter_end()`, `is_year_end()` for signal and rebalance logic
- **Settlement & expiry** — `T+N` conventions, COB roll-back, and monthly/quarterly/weekly expiry dates
- **Pluggable calendars** — load a custom JSON calendar file and set it as the active default with one call

---

## Installation

```bash
pip install quando
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add quando
```

For development:

```bash
git clone https://github.com/aexsalomao/quando
cd quando
uv sync --extra dev
```

---

## Quick Start

```python
import quando as q

q.use("NYSE")  # set global calendar (default if omitted)

# Parse anything
q.to_datetime("20240115")             # datetime(2024, 1, 15, tzinfo=UTC)
q.to_datetime(45306)                  # Excel West serial → 2024-01-15
q.to_datetime(1705276800.0)           # Unix epoch

# Day checks
q.is_business_day("2024-01-15")       # False — MLK Day
q.is_holiday("2024-01-15")            # True
q.is_weekend("2024-01-13")            # True

# Navigation
q.next_business_day("2024-12-24")     # Dec 26 (Christmas skip)
q.add_business_days("2024-01-10", 5)  # Jan 17
q.snap("2024-01-13", "forward")       # Jan 15... wait, holiday → Jan 16

# Period boundaries
q.start_of_month("2024-09-15")        # Sep 3 (Sep 1 is Sunday, Sep 2 is Labor Day)
q.end_of_quarter("2024-01-15")        # Mar 28 (Mar 31 is Sunday, Mar 29 Good Friday)
q.end_of_year("2024-06-01")           # Dec 31

# Rebalancing triggers
if q.is_month_end("2024-01-31"):
    print("rebalance!")               # prints — Jan 31 is last NYSE trading day

# Date ranges & counting
q.date_range("2024-01-01", "2024-01-31")   # list of 21 trading days
q.trading_days_in_year(2024)               # 252
q.business_days_between("2024-01-01", "2024-01-31")  # 21

# Settlement & expiry
q.to_settlement_date("2024-06-10", "T+2")  # Jun 12
q.next_expiry("2024-01-01", "monthly")     # Jan 19 (third Friday)
q.days_to_expiry("2024-01-10", "2024-01-19")  # 6 business days
```

---

## API

### Setup

| Call | Returns | Notes |
|---|---|---|
| `q.use(cal)` | `None` | Set global calendar: `"NYSE"`, `"LSE"`, `"EUREX"`, … |
| `q.verbose(flag)` | `None` | Toggle internal debug logging |
| `q.as_of(value)` | `None` | Set reference date for expiry/settlement calculations |

### Conversions

| Call | Returns |
|---|---|
| `q.to_timestamp(value)` | `float` — Unix epoch |
| `q.to_datetime(value)` | `datetime` — UTC-aware |
| `q.to_west(value)` | `int` — Excel serial (days since 1899-12-30) |
| `q.to_iso(value)` | `str` — ISO 8601 (`YYYY-MM-DDTHH:MM:SS+00:00`) |
| `q.convert(value, to_fmt)` | any — `to_fmt` ∈ `"timestamp"`, `"datetime"`, `"west"`, `"iso"` |
| `q.to_timestamps(values)` | `list[float]` |
| `q.to_datetimes(values)` | `list[datetime]` |

### Timezone

| Call | Returns |
|---|---|
| `q.shift_tz(value, tz)` | `datetime` — clock converted to target timezone |
| `q.localize(value, tz)` | `datetime` — timezone attached, clock unchanged |
| `q.strip_tz(value)` | `datetime` — naive, expressed in UTC |

### Validation & Comparison

| Call | Returns |
|---|---|
| `q.is_valid(value)` | `bool` — True if quando can parse the input |
| `q.is_same_day(a, b)` | `bool` |
| `q.is_before(a, b)` | `bool` — True if `a < b` |
| `q.is_after(a, b)` | `bool` — True if `a > b` |

### Day Checks

| Call | Returns |
|---|---|
| `q.is_weekend(value)` | `bool` — no calendar needed |
| `q.is_holiday(value, cal=None)` | `bool` — weekday that is a market holiday |
| `q.is_business_day(value, cal=None)` | `bool` — not weekend and not holiday |
| `q.is_expiry_day(value)` | `bool` — third Friday of the month |
| `q.day_of_week(value)` | `str` — e.g. `"Monday"` |

### Holiday Management

| Call | Returns |
|---|---|
| `q.list_holidays(year, cal=None)` | `list[tuple[date, str]]` — sorted `(date, name)` pairs |
| `q.add_holiday(value, name, cal=None)` | `None` — add a custom holiday override |
| `q.remove_holiday(value, cal=None)` | `None` — remove a holiday from the active calendar |

### Date Navigation

| Call | Returns |
|---|---|
| `q.next_business_day(value, cal=None)` | `datetime` |
| `q.prev_business_day(value, cal=None)` | `datetime` |
| `q.add_business_days(value, n, cal=None)` | `datetime` — negative `n` goes backward |
| `q.snap(value, direction, cal=None)` | `datetime` — `direction` ∈ `"forward"`, `"backward"`, `"nearest"` |

### Date Ranges & Counting

| Call | Returns |
|---|---|
| `q.business_days_between(start, end, cal=None)` | `int` — exclusive of both endpoints |
| `q.date_range(start, end, cal=None)` | `list[datetime]` — all business days, inclusive |
| `q.trading_days_in_month(value, cal=None)` | `int` |
| `q.trading_days_in_year(year, cal=None)` | `int` — annualization factor (typically 252) |
| `q.filter_business_days(values, cal=None)` | `list` — only the business days from input |

### Period Boundaries

All period functions return a UTC-aware `datetime` that lands on a business day.

| Call | Returns |
|---|---|
| `q.start_of_month(value, cal=None)` | `datetime` — first business day of month |
| `q.end_of_month(value, cal=None)` | `datetime` — last business day of month |
| `q.start_of_quarter(value, cal=None)` | `datetime` — first business day of quarter |
| `q.end_of_quarter(value, cal=None)` | `datetime` — last business day of quarter |
| `q.start_of_year(value, cal=None)` | `datetime` — first business day of year |
| `q.end_of_year(value, cal=None)` | `datetime` — last business day of year |
| `q.start_of_week(value, cal=None)` | `datetime` — first business day of ISO week |
| `q.end_of_week(value, cal=None)` | `datetime` — last business day of ISO week |

### Period Boundary Checks

Useful as rebalancing triggers in a backtest loop.

| Call | Returns |
|---|---|
| `q.is_month_end(value, cal=None)` | `bool` — True if value is the last business day of its month |
| `q.is_quarter_end(value, cal=None)` | `bool` — True if value is the last business day of its quarter |
| `q.is_year_end(value, cal=None)` | `bool` — True if value is the last business day of its year |

### Settlement & Expiry

| Call | Returns |
|---|---|
| `q.to_settlement_date(value, convention, cal=None)` | `datetime` — e.g. `convention="T+2"` adds 2 business days |
| `q.to_cob(value, cal=None)` | `datetime` — close-of-business; rolls back if non-business day |
| `q.next_expiry(value, contract_type)` | `datetime` — `contract_type` ∈ `"monthly"`, `"quarterly"`, `"weekly"` |
| `q.days_to_expiry(value, expiry, cal=None)` | `int` — business days to expiry |

### Reference & I/O

| Call | Returns |
|---|---|
| `q.today(cal=None)` | `datetime` — today, tz-aware in the exchange's local timezone |
| `q.load_calendar(path)` | `None` — load JSON calendar file and set as active |
| `q.save_calendar(path, cal=None)` | `None` — export custom holiday additions to JSON |

---

## Supported Calendars

| Alias | Exchange | Timezone |
|---|---|---|
| `NYSE` | New York Stock Exchange | America/New_York |
| `EUREX` | Eurex | Europe/Berlin |
| `LSE` | London Stock Exchange | Europe/London |
| `TSX` | Toronto Stock Exchange | America/Toronto |
| `ASX` | Australian Securities Exchange | Australia/Sydney |
| `HKEX` | Hong Kong Exchanges | Asia/Hong_Kong |
| `JPX` | Japan Exchange Group | Asia/Tokyo |
| `CME` | Chicago Mercantile Exchange | America/Chicago |

Any `exchange-calendars` exchange code (e.g. `"XLON"`, `"XEUR"`) also works directly.

---

## Custom Calendars

```python
import quando as q

# Add a one-off closure
q.use("NYSE")
q.add_holiday("2024-07-05", "Independence Day (observed)")

# Persist to JSON
q.save_calendar("my_calendar.json")

# Load it back in another session
q.load_calendar("my_calendar.json")  # also calls q.use() with the saved calendar name
```

JSON schema:

```json
{
  "name": "NYSE",
  "holidays": [
    {"date": "2024-07-05", "name": "Independence Day (observed)"}
  ]
}
```

---

## Running Tests

```bash
pytest
pytest --cov=quando   # with coverage
```

---

## License

MIT © [Antônio Salomão](https://github.com/aexsalomao)
