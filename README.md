# quando

Time translation & holiday tracking for backtesting pipelines.

```python
import quando as q

q.use("NYSE")

q.to_datetime("20240115")           # datetime(2024, 1, 15, tzinfo=UTC)
q.next_business_day("2024-12-24")   # skip Christmas Eve -> Dec 26
q.date_range("2024-01-01", "2024-01-31")  # all NYSE trading days in Jan
q.to_settlement_date("2024-06-10", "T+2") # Jun 12
q.next_expiry("2024-01-01", "monthly")    # Jan 19 (third Friday)
q.trading_days_in_year(2024)        # 252
```

## Install

```bash
pip install quando
```

## Key features

- **42 methods** covering conversion, timezone, validation, day checks, navigation, ranges, period boundaries, settlement, and expiry
- **Auto-detects input type**: string, datetime, int/float (Unix epoch), date object
- **Market calendars** via `exchange-calendars` (NYSE, EUREX, LSE, TSX, ASX, HKEX, JPX, CME + any exchange code)
- **Custom holidays**: add, remove, load from / save to JSON
- `cal=None` always falls back to the global calendar set by `q.use()`

## Supported formats

| Name | Example |
|------|---------|
| ISO 8601 | `"2024-01-15"` |
| West (American) | `"01/15/2024"` |
| Compact | `"20240115"` |
| Unix epoch | `1705276800.0` |
| Python datetime | `datetime(2024, 1, 15)` |

See [CLAUDE.md](CLAUDE.md) for the full API reference.

## License

MIT
