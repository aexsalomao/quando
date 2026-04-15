# quando — API Reference

## Conventions
- All inputs are auto-detected: string, datetime, int/float (Unix epoch), date
- `cal=None` falls back to the global calendar set by `q.use()`
- Default calendar is **NYSE** (logs a one-time notice if `q.use()` was never called)
- "West" format = Excel serial integer (days since 1899-12-30). ISO = `YYYY-MM-DDTHH:MM:SS+00:00`
- All returned datetimes are UTC-aware unless a timezone is explicitly attached

---

## Setup
| Call | Returns | Notes |
|------|---------|-------|
| `q.use(cal: str)` | `None` | Set global calendar. e.g. `"NYSE"`, `"EUREX"`, `"LSE"` |
| `q.verbose(flag: bool)` | `None` | Toggle internal logging |
| `q.as_of(value)` | `None` | Set global reference date for expiry/settlement |

## Conversions
| Call | Returns |
|------|---------|
| `q.to_timestamp(value)` | `float` — Unix epoch |
| `q.to_datetime(value)` | `datetime` — UTC-aware |
| `q.to_west(value)` | `int` — Excel serial date (days since 1899-12-30, e.g. 45306) |
| `q.to_iso(value)` | `str` — ISO 8601 |
| `q.convert(value, to_fmt)` | any — `to_fmt` ∈ `"timestamp"`, `"datetime"`, `"west"`, `"iso"` |
| `q.to_timestamps(values)` | `list[float]` |
| `q.to_datetimes(values)` | `list[datetime]` |

## Timezone
| Call | Returns |
|------|---------|
| `q.shift_tz(value, tz: str)` | `datetime` — converted to target tz |
| `q.localize(value, tz: str)` | `datetime` — tz attached, clock unchanged |
| `q.strip_tz(value)` | `datetime` — naive, expressed in UTC |

## Validation & Comparison
| Call | Returns |
|------|---------|
| `q.is_valid(value)` | `bool` |
| `q.is_same_day(a, b)` | `bool` |
| `q.is_before(a, b)` | `bool` — True if a < b |
| `q.is_after(a, b)` | `bool` — True if a > b |

## Day Checks
| Call | Returns |
|------|---------|
| `q.is_weekend(value)` | `bool` — no calendar needed |
| `q.is_holiday(value, cal=None)` | `bool` — weekday that is a market holiday |
| `q.is_business_day(value, cal=None)` | `bool` — not weekend and not holiday |
| `q.is_expiry_day(value)` | `bool` — third Friday of the month |
| `q.day_of_week(value)` | `str` — e.g. `"Monday"` |

## Holiday Calendar Management
| Call | Returns |
|------|---------|
| `q.list_holidays(year: int, cal=None)` | `list[tuple[date, str]]` — `(date, name)` pairs |
| `q.add_holiday(value, name: str, cal=None)` | `None` |
| `q.remove_holiday(value, cal=None)` | `None` |

## Date Navigation
| Call | Returns |
|------|---------|
| `q.next_business_day(value, cal=None)` | `datetime` |
| `q.prev_business_day(value, cal=None)` | `datetime` |
| `q.add_business_days(value, n: int, cal=None)` | `datetime` — negative n goes backward |
| `q.snap(value, direction, cal=None)` | `datetime` — `direction` ∈ `"forward"`, `"backward"`, `"nearest"` |

## Date Ranges & Counting
| Call | Returns |
|------|---------|
| `q.business_days_between(start, end, cal=None)` | `int` — exclusive of endpoints |
| `q.date_range(start, end, cal=None)` | `list[datetime]` — business days inclusive |
| `q.trading_days_in_month(value, cal=None)` | `int` |
| `q.trading_days_in_year(year: int, cal=None)` | `int` — useful as annualization factor |
| `q.filter_business_days(values, cal=None)` | `list` — only the business days from input |

## Period Boundaries  (all return business days)
| Call | Returns |
|------|---------|
| `q.start_of_month(value, cal=None)` | `datetime` — first business day of month |
| `q.end_of_month(value, cal=None)` | `datetime` — last business day of month |
| `q.start_of_quarter(value, cal=None)` | `datetime` |
| `q.end_of_quarter(value, cal=None)` | `datetime` |

## Settlement & Expiry
| Call | Returns |
|------|---------|
| `q.to_settlement_date(value, convention, cal=None)` | `datetime` — `convention` e.g. `"T+2"` |
| `q.to_cob(value, cal=None)` | `datetime` — COB date; rolls back if non-business day |
| `q.next_expiry(value, contract_type)` | `datetime` — `contract_type` ∈ `"monthly"`, `"quarterly"`, `"weekly"` |
| `q.days_to_expiry(value, expiry, cal=None)` | `int` — business days to expiry |

## Reference
| Call | Returns |
|------|---------|
| `q.today(cal=None)` | `datetime` — today, tz-aware in the calendar's exchange timezone |

## I/O
| Call | Returns |
|------|---------|
| `q.load_calendar(path: str)` | `None` — loads JSON, sets as active calendar |
| `q.save_calendar(path: str, cal=None)` | `None` — exports custom holidays to JSON |

---

## Supported Calendars
`NYSE`, `EUREX`, `LSE`, `TSX`, `ASX`, `HKEX`, `JPX`, `CME`
(backed by `exchange-calendars`; any exchange code it supports also works)

## JSON Calendar Schema
```json
{
  "name": "MY_CAL",
  "holidays": [
    {"date": "2024-07-04", "name": "Independence Day"},
    {"date": "2024-12-26", "name": "Boxing Day"}
  ]
}
```
