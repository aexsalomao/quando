"""
quando — time translation & holiday tracking for backtesting pipelines

    import quando as q

    q.use("NYSE")
    q.to_datetime("2024-01-15")
    q.next_business_day("2024-12-24")
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from quando._state import use, verbose, as_of, get_tz

from quando._convert import (
    to_timestamp,
    to_datetime,
    to_west,
    to_iso,
    convert,
    to_timestamps,
    to_datetimes,
)

from quando._timezone import shift_tz, localize, strip_tz

from quando._validate import is_valid, is_same_day, is_before, is_after

from quando._checks import (
    is_weekend,
    is_holiday,
    is_business_day,
    is_expiry_day,
    day_of_week,
)

from quando._calendar import list_holidays, add_holiday, remove_holiday

from quando._navigate import (
    next_business_day,
    prev_business_day,
    add_business_days,
    snap,
)

from quando._ranges import (
    business_days_between,
    date_range,
    trading_days_in_month,
    trading_days_in_year,
    filter_business_days,
)

from quando._periods import (
    start_of_month,
    end_of_month,
    start_of_quarter,
    end_of_quarter,
    start_of_year,
    end_of_year,
    start_of_week,
    end_of_week,
    is_month_end,
    is_quarter_end,
    is_year_end,
)

from quando._settlement import (
    to_settlement_date,
    to_cob,
    next_expiry,
    days_to_expiry,
)

from quando._io import load_calendar, save_calendar


def today(cal=None) -> datetime:
    """Today as a timezone-aware datetime in the active calendar's exchange timezone."""
    tz = ZoneInfo(get_tz(cal))
    now = datetime.now(tz=tz)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


__all__ = [
    # setup
    "use", "verbose", "as_of",
    # conversions
    "to_timestamp", "to_datetime", "to_west", "to_iso", "convert",
    "to_timestamps", "to_datetimes",
    # timezone
    "shift_tz", "localize", "strip_tz",
    # validation
    "is_valid", "is_same_day", "is_before", "is_after",
    # day checks
    "is_weekend", "is_holiday", "is_business_day", "is_expiry_day", "day_of_week",
    # holiday management
    "list_holidays", "add_holiday", "remove_holiday",
    # navigation
    "next_business_day", "prev_business_day", "add_business_days", "snap",
    # ranges
    "business_days_between", "date_range", "trading_days_in_month",
    "trading_days_in_year", "filter_business_days",
    # periods
    "start_of_month", "end_of_month",
    "start_of_quarter", "end_of_quarter",
    "start_of_year", "end_of_year",
    "start_of_week", "end_of_week",
    # period boundary checks
    "is_month_end", "is_quarter_end", "is_year_end",
    # settlement & expiry
    "to_settlement_date", "to_cob", "next_expiry", "days_to_expiry",
    # reference
    "today",
    # I/O
    "load_calendar", "save_calendar",
]
