"""
Holiday calendar management: exchange_calendars data + custom overrides.
"""

import logging
from datetime import date
from functools import lru_cache

from quando._parse import DateLike, parse
from quando._state import get_cal, get_xcal_name

logger = logging.getLogger(__name__)

# {cal_name: {date: holiday_name}}
_CUSTOM_ADD: dict[str, dict[date, str]] = {}
# {cal_name: set[date]}
_CUSTOM_REMOVE: dict[str, set[date]] = {}


def _norm(cal: str | None = None) -> str:
    return get_cal(cal)


@lru_cache(maxsize=256)
def _xcal_holidays(xcal_name: str, year: int) -> tuple[tuple[date, str], ...]:
    """
    Fetch named holidays from exchange_calendars for a year.
    Returns a tuple of (date, name) pairs (hashable for lru_cache).
    """
    try:
        import exchange_calendars as xcals
        import pandas as pd
    except ImportError:
        logger.warning(
            "quando: exchange_calendars/pandas not installed — holiday data unavailable for %s",
            xcal_name,
        )
        return ()

    try:
        xc = xcals.get_calendar(xcal_name)
    except Exception as exc:
        # Unknown exchange code — xcals raises various error types; surface as warning
        # rather than fail hard so downstream `is_business_day` still handles weekends.
        logger.warning("quando: could not load calendar '%s': %s", xcal_name, exc)
        return ()

    start = pd.Timestamp(f"{year}-01-01")
    end = pd.Timestamp(f"{year}-12-31")
    series = xc.regular_holidays.holidays(start=start, end=end, return_name=True)
    result = {ts.date(): name for ts, name in series.items()}
    for ts in getattr(xc, "adhoc_holidays", []):
        d = pd.Timestamp(ts).date()
        if start.date() <= d <= end.date() and d not in result:
            result[d] = "Adhoc Holiday"
    return tuple(sorted(result.items()))


def _base_holidays(cal_name: str, year: int) -> dict[date, str]:
    xcal_name = get_xcal_name(cal_name)
    return dict(_xcal_holidays(xcal_name, year))


def get_holidays_for_year(cal_name: str, year: int) -> dict[date, str]:
    """Merged {date: name} for the year, respecting custom add/remove."""
    base = _base_holidays(cal_name, year)
    for d in _CUSTOM_REMOVE.get(cal_name, set()):
        base.pop(d, None)
    for d, name in _CUSTOM_ADD.get(cal_name, {}).items():
        if d.year == year:
            base[d] = name
    return base


def is_holiday_date(d: date, cal_name: str) -> bool:
    return d in get_holidays_for_year(cal_name, d.year)


# ── public API ────────────────────────────────────────────────────────────────


def list_holidays(year: int, cal: str | None = None) -> list[tuple[date, str]]:
    """Return [(date, name), ...] sorted by date."""
    return sorted(get_holidays_for_year(_norm(cal), year).items())


def add_holiday(value: DateLike, name: str, cal: str | None = None) -> None:
    cal_name = _norm(cal)
    d = parse(value).date()
    _CUSTOM_ADD.setdefault(cal_name, {})[d] = name
    _xcal_holidays.cache_clear()


def remove_holiday(value: DateLike, cal: str | None = None) -> None:
    cal_name = _norm(cal)
    d = parse(value).date()
    _CUSTOM_REMOVE.setdefault(cal_name, set()).add(d)
    # Also scrub from custom additions so re-adding logic doesn't win
    _CUSTOM_ADD.get(cal_name, {}).pop(d, None)
    _xcal_holidays.cache_clear()
