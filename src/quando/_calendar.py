"""
Holiday calendar management: exchange_calendars data + custom overrides.
"""
from datetime import date
from functools import lru_cache

# {cal_name: {date: holiday_name}}
_CUSTOM_ADD: dict = {}
# {cal_name: set[date]}
_CUSTOM_REMOVE: dict = {}


def _norm(cal=None) -> str:
    from quando._state import get_cal
    return get_cal(cal)


@lru_cache(maxsize=256)
def _xcal_holidays(xcal_name: str, year: int) -> tuple:
    """
    Fetch named holidays from exchange_calendars for a year.
    Returns a tuple of (date, name) pairs (hashable for lru_cache).
    """
    try:
        import exchange_calendars as xcals
        import pandas as pd
        xc = xcals.get_calendar(xcal_name)
        start = pd.Timestamp(f"{year}-01-01")
        end   = pd.Timestamp(f"{year}-12-31")
        series = xc.regular_holidays.holidays(start=start, end=end, return_name=True)
        result = {ts.date(): name for ts, name in series.items()}
        for ts in getattr(xc, "adhoc_holidays", []):
            d = pd.Timestamp(ts).date()
            if start.date() <= d <= end.date() and d not in result:
                result[d] = "Adhoc Holiday"
        return tuple(sorted(result.items()))
    except Exception:
        return ()


def _base_holidays(cal_name: str, year: int) -> dict:
    from quando._state import get_xcal_name
    xcal_name = get_xcal_name(cal_name)
    return dict(_xcal_holidays(xcal_name, year))


def get_holidays_for_year(cal_name: str, year: int) -> dict:
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

def list_holidays(year: int, cal=None) -> list:
    """Return [(date, name), ...] sorted by date."""
    return sorted(get_holidays_for_year(_norm(cal), year).items())


def add_holiday(value, name: str, cal=None) -> None:
    from quando._parse import parse
    cal_name = _norm(cal)
    d = parse(value).date()
    _CUSTOM_ADD.setdefault(cal_name, {})[d] = name
    _xcal_holidays.cache_clear()


def remove_holiday(value, cal=None) -> None:
    from quando._parse import parse
    cal_name = _norm(cal)
    d = parse(value).date()
    _CUSTOM_REMOVE.setdefault(cal_name, set()).add(d)
    _xcal_holidays.cache_clear()
