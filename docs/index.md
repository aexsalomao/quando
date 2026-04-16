---
hide:
  - navigation
  - toc
---

<div align="center" markdown>

# quando

**Navigate trading calendars, business days, and market periods — with zero fuss.**

[![PyPI](https://img.shields.io/pypi/v/quando?color=blue)](https://pypi.org/project/quando/)
[![Python](https://img.shields.io/pypi/pyversions/quando)](https://pypi.org/project/quando/)
[![License](https://img.shields.io/github/license/aexsalomao/quando)](https://github.com/aexsalomao/quando/blob/master/LICENSE)
[![CI](https://github.com/aexsalomao/quando/actions/workflows/ci.yml/badge.svg)](https://github.com/aexsalomao/quando/actions/workflows/ci.yml)
[![Docs](https://github.com/aexsalomao/quando/actions/workflows/docs.yml/badge.svg)](https://aexsalomao.github.io/quando/)

```bash
pip install quando
```

</div>

---

## Features

<div class="grid cards" markdown>

-   :material-calendar-check:{ .lg .middle } **52 methods, one import**

    ---

    Conversions, timezone, validation, day checks, navigation, ranges, period boundaries, settlement, and expiry — all under `import quando as q`.

    [:octicons-arrow-right-24: API Reference](api.md)

-   :material-auto-fix:{ .lg .middle } **Auto-detecting inputs**

    ---

    Pass a string, `datetime`, `date`, Unix epoch, or Excel West serial — quando figures it out. No manual parsing.

-   :material-earth:{ .lg .middle } **8 exchange calendars**

    ---

    NYSE, EUREX, LSE, TSX, ASX, HKEX, JPX, CME — or any `exchange-calendars` code. Switch with a single `q.use()` call.

-   :material-calendar-edit:{ .lg .middle } **Custom holidays**

    ---

    Add or remove holidays, persist overrides to JSON, and load them back in any session. Merged transparently at query time.

-   :material-repeat:{ .lg .middle } **Rebalancing triggers**

    ---

    `is_month_end()`, `is_quarter_end()`, `is_year_end()` — drop-in conditions for backtest rebalancing logic.

-   :material-swap-horizontal:{ .lg .middle } **Settlement & expiry**

    ---

    `T+N` conventions, COB roll-back, and monthly/quarterly/weekly expiry dates for derivatives workflows.

</div>

---

## Quick start

=== "Day checks"

    ```python
    import quando as q

    q.use("NYSE")  # set global calendar (default: NYSE)

    q.is_business_day("2024-01-15")   # False — MLK Day
    q.is_holiday("2024-01-15")        # True
    q.is_weekend("2024-01-13")        # True
    q.day_of_week("2024-01-15")       # "Monday"
    ```

=== "Navigation"

    ```python
    import quando as q

    q.next_business_day("2024-12-24")       # Dec 26 (Christmas skip)
    q.prev_business_day("2024-01-01")       # Dec 29, 2023
    q.add_business_days("2024-01-10", 5)    # Jan 17
    q.snap("2024-01-13", "forward")         # Jan 16 (weekend + MLK)
    ```

=== "Period boundaries"

    ```python
    import quando as q

    q.start_of_month("2024-09-15")     # Sep 3 (Sep 1 Sunday, Sep 2 Labor Day)
    q.end_of_quarter("2024-01-15")     # Mar 28 (Mar 31 Sunday, Mar 29 Good Friday)
    q.end_of_year("2024-06-01")        # Dec 31

    # Rebalancing trigger
    if q.is_month_end("2024-01-31"):
        print("rebalance!")            # prints — Jan 31 is last NYSE trading day
    ```

=== "Settlement & expiry"

    ```python
    import quando as q

    q.to_settlement_date("2024-06-10", "T+2")      # Jun 12
    q.to_cob("2024-01-13")                         # Jan 12 (weekend → roll back)
    q.next_expiry("2024-01-01", "monthly")          # Jan 19 (third Friday)
    q.days_to_expiry("2024-01-10", "2024-01-19")   # 6 business days
    ```

=== "Custom calendars"

    ```python
    import quando as q

    q.use("NYSE")
    q.add_holiday("2024-07-05", "Independence Day (observed)")

    # Persist to JSON
    q.save_calendar("my_calendar.json")

    # Load it back in another session
    q.load_calendar("my_calendar.json")
    ```

<div align="center" markdown>

[:octicons-arrow-right-24: Full API Reference](api.md){ .md-button .md-button--primary }
[:octicons-arrow-right-24: Contributing](contributing.md){ .md-button }

</div>

---

## Supported calendars

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
