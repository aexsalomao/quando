# API Reference

## Setup

```python
import quando as q

q.use("NYSE")  # set global calendar; default is NYSE
```

| Call | Description |
|---|---|
| `q.use(cal)` | Set global calendar: `"NYSE"`, `"LSE"`, `"EUREX"`, … |
| `q.verbose(flag)` | Toggle internal debug logging |
| `q.as_of(value)` | Set reference date for expiry/settlement calculations |

---

## Conversions

Accepts any date-like input: ISO string, compact string, `datetime`, `date`, Unix epoch (`int`/`float`), or Excel West serial.

| Call | Returns |
|---|---|
| `q.to_timestamp(value)` | `float` — Unix epoch |
| `q.to_datetime(value)` | `datetime` — UTC-aware |
| `q.to_west(value)` | `int` — Excel serial (days since 1899-12-30) |
| `q.to_iso(value)` | `str` — ISO 8601 (`YYYY-MM-DDTHH:MM:SS+00:00`) |
| `q.convert(value, to_fmt)` | any — `to_fmt` ∈ `"timestamp"`, `"datetime"`, `"west"`, `"iso"` |
| `q.to_timestamps(values)` | `list[float]` — batch conversion |
| `q.to_datetimes(values)` | `list[datetime]` — batch conversion |

---

## Timezone

| Call | Returns |
|---|---|
| `q.shift_tz(value, tz)` | `datetime` — clock converted to target timezone |
| `q.localize(value, tz)` | `datetime` — timezone attached, clock unchanged |
| `q.strip_tz(value)` | `datetime` — naive, expressed in UTC |

---

## Validation & Comparison

| Call | Returns |
|---|---|
| `q.is_valid(value)` | `bool` — True if quando can parse the input |
| `q.is_same_day(a, b)` | `bool` |
| `q.is_before(a, b)` | `bool` — True if `a < b` |
| `q.is_after(a, b)` | `bool` — True if `a > b` |

---

## Day Checks

| Call | Returns |
|---|---|
| `q.is_weekend(value)` | `bool` — no calendar needed |
| `q.is_holiday(value, cal=None)` | `bool` — weekday that is a market holiday |
| `q.is_business_day(value, cal=None)` | `bool` — not weekend and not holiday |
| `q.is_expiry_day(value)` | `bool` — third Friday of the month |
| `q.day_of_week(value)` | `str` — e.g. `"Monday"` |

---

## Holiday Management

| Call | Returns |
|---|---|
| `q.list_holidays(year, cal=None)` | `list[tuple[date, str]]` — sorted `(date, name)` pairs |
| `q.add_holiday(value, name, cal=None)` | `None` — add a custom holiday override |
| `q.remove_holiday(value, cal=None)` | `None` — remove a holiday from the active calendar |

---

## Date Navigation

| Call | Returns |
|---|---|
| `q.next_business_day(value, cal=None)` | `datetime` |
| `q.prev_business_day(value, cal=None)` | `datetime` |
| `q.add_business_days(value, n, cal=None)` | `datetime` — negative `n` goes backward |
| `q.snap(value, direction, cal=None)` | `datetime` — `direction` ∈ `"forward"`, `"backward"`, `"nearest"` |

---

## Date Ranges & Counting

| Call | Returns |
|---|---|
| `q.business_days_between(start, end, cal=None)` | `int` — exclusive of both endpoints |
| `q.date_range(start, end, cal=None)` | `list[datetime]` — all business days, inclusive |
| `q.trading_days_in_month(value, cal=None)` | `int` |
| `q.trading_days_in_year(year, cal=None)` | `int` — annualization factor (typically 252) |
| `q.filter_business_days(values, cal=None)` | `list` — only the business days from input |

---

## Period Boundaries

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

---

## Period Boundary Checks

Useful as rebalancing triggers in a backtest loop.

| Call | Returns |
|---|---|
| `q.is_month_end(value, cal=None)` | `bool` — True if value is the last business day of its month |
| `q.is_quarter_end(value, cal=None)` | `bool` — True if value is the last business day of its quarter |
| `q.is_year_end(value, cal=None)` | `bool` — True if value is the last business day of its year |

---

## Settlement & Expiry

| Call | Returns |
|---|---|
| `q.to_settlement_date(value, convention, cal=None)` | `datetime` — e.g. `convention="T+2"` adds 2 business days |
| `q.to_cob(value, cal=None)` | `datetime` — close-of-business; rolls back if non-business day |
| `q.next_expiry(value, contract_type)` | `datetime` — `contract_type` ∈ `"monthly"`, `"quarterly"`, `"weekly"` |
| `q.days_to_expiry(value, expiry, cal=None)` | `int` — business days to expiry |

---

## Reference & I/O

| Call | Returns |
|---|---|
| `q.today(cal=None)` | `datetime` — today, tz-aware in the exchange's local timezone |
| `q.load_calendar(path)` | `None` — load JSON calendar file and set as active |
| `q.save_calendar(path, cal=None)` | `None` — export custom holiday additions to JSON |

### Custom Calendar JSON Schema

```json
{
  "name": "NYSE",
  "holidays": [
    {"date": "2024-07-05", "name": "Independence Day (observed)"}
  ]
}
```
