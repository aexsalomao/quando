# quando

> Navigate trading calendars, business days, and market periods — with zero fuss.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)
[![CI](https://github.com/aexsalomao/quando/actions/workflows/ci.yml/badge.svg)](https://github.com/aexsalomao/quando/actions/workflows/ci.yml)

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

# Period boundaries
q.start_of_month("2024-09-15")        # Sep 3 (Sep 1 is Sunday, Sep 2 is Labor Day)
q.end_of_quarter("2024-01-15")        # Mar 28
q.end_of_year("2024-06-01")           # Dec 31

# Rebalancing triggers
if q.is_month_end("2024-01-31"):
    print("rebalance!")               # prints — Jan 31 is last NYSE trading day

# Date ranges & counting
q.date_range("2024-01-01", "2024-01-31")          # list of 21 trading days
q.trading_days_in_year(2024)                       # 252
q.business_days_between("2024-01-01", "2024-01-31")  # 21

# Settlement & expiry
q.to_settlement_date("2024-06-10", "T+2")          # Jun 12
q.next_expiry("2024-01-01", "monthly")             # Jan 19 (third Friday)
q.days_to_expiry("2024-01-10", "2024-01-19")       # 6 business days
```

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

## License

MIT © [Antônio Salomão](https://github.com/aexsalomao)
