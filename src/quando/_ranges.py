from datetime import datetime, timedelta, timezone
import calendar as _cal_mod

from quando._parse import parse, DateLike
from quando._checks import is_business_day


def business_days_between(start: DateLike, end: DateLike, cal: str | None = None) -> int:
    """Count business days strictly between start and end (exclusive)."""
    s, e = parse(start), parse(end)
    if s >= e:
        return 0
    count = 0
    cur = s + timedelta(days=1)
    while cur < e:
        if is_business_day(cur, cal):
            count += 1
        cur += timedelta(days=1)
    return count


def date_range(start: DateLike, end: DateLike, cal: str | None = None) -> list[datetime]:
    """All business days between start and end, inclusive."""
    s, e = parse(start), parse(end)
    result, cur = [], s
    while cur <= e:
        if is_business_day(cur, cal):
            result.append(cur)
        cur += timedelta(days=1)
    return result


def trading_days_in_month(value: DateLike, cal: str | None = None) -> int:
    dt = parse(value)
    days_in_month = _cal_mod.monthrange(dt.year, dt.month)[1]
    return sum(
        1
        for day in range(1, days_in_month + 1)
        if is_business_day(datetime(dt.year, dt.month, day, tzinfo=timezone.utc), cal)
    )


def trading_days_in_year(year: int, cal: str | None = None) -> int:
    cur = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year, 12, 31, tzinfo=timezone.utc)
    count = 0
    while cur <= end:
        if is_business_day(cur, cal):
            count += 1
        cur += timedelta(days=1)
    return count


def filter_business_days(values: list[DateLike], cal: str | None = None) -> list[DateLike]:
    return [v for v in values if is_business_day(parse(v), cal)]
