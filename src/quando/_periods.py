from datetime import datetime, timedelta, timezone
import calendar as _cal_mod

from quando._parse import parse
from quando._checks import is_business_day
from quando._navigate import next_business_day, prev_business_day


def start_of_month(value, cal=None) -> datetime:
    dt = parse(value)
    first = datetime(dt.year, dt.month, 1, tzinfo=timezone.utc)
    return first if is_business_day(first, cal) else next_business_day(first, cal)


def end_of_month(value, cal=None) -> datetime:
    dt = parse(value)
    last_day = _cal_mod.monthrange(dt.year, dt.month)[1]
    last = datetime(dt.year, dt.month, last_day, tzinfo=timezone.utc)
    return last if is_business_day(last, cal) else prev_business_day(last, cal)


def start_of_quarter(value, cal=None) -> datetime:
    dt = parse(value)
    q_start_month = ((dt.month - 1) // 3) * 3 + 1
    first = datetime(dt.year, q_start_month, 1, tzinfo=timezone.utc)
    return first if is_business_day(first, cal) else next_business_day(first, cal)


def end_of_quarter(value, cal=None) -> datetime:
    dt = parse(value)
    q_end_month = ((dt.month - 1) // 3) * 3 + 3
    last_day = _cal_mod.monthrange(dt.year, q_end_month)[1]
    last = datetime(dt.year, q_end_month, last_day, tzinfo=timezone.utc)
    return last if is_business_day(last, cal) else prev_business_day(last, cal)


def start_of_year(value, cal=None) -> datetime:
    dt = parse(value)
    first = datetime(dt.year, 1, 1, tzinfo=timezone.utc)
    return first if is_business_day(first, cal) else next_business_day(first, cal)


def end_of_year(value, cal=None) -> datetime:
    dt = parse(value)
    last = datetime(dt.year, 12, 31, tzinfo=timezone.utc)
    return last if is_business_day(last, cal) else prev_business_day(last, cal)


def start_of_week(value, cal=None) -> datetime:
    """First business day of the ISO week (Mon–Fri) containing value."""
    dt = parse(value)
    monday = (dt - timedelta(days=dt.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return monday if is_business_day(monday, cal) else next_business_day(monday, cal)


def end_of_week(value, cal=None) -> datetime:
    """Last business day of the ISO week (Mon–Fri) containing value."""
    dt = parse(value)
    friday = (dt - timedelta(days=dt.weekday()) + timedelta(days=4)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return friday if is_business_day(friday, cal) else prev_business_day(friday, cal)


def is_month_end(value, cal=None) -> bool:
    """True if value is the last business day of its month."""
    dt = parse(value)
    return dt.date() == end_of_month(dt, cal).date()


def is_quarter_end(value, cal=None) -> bool:
    """True if value is the last business day of its quarter."""
    dt = parse(value)
    return dt.date() == end_of_quarter(dt, cal).date()


def is_year_end(value, cal=None) -> bool:
    """True if value is the last business day of its year."""
    dt = parse(value)
    return dt.date() == end_of_year(dt, cal).date()
