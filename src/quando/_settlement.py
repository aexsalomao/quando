from datetime import datetime, timedelta, timezone
import re

from quando._parse import parse, DateLike
from quando._navigate import add_business_days, prev_business_day
from quando._checks import is_business_day
from quando._ranges import business_days_between


def to_settlement_date(value: DateLike, convention: str, cal: str | None = None) -> datetime:
    """
    Given a trade date and a convention like 'T+2', return the settlement date
    by adding N business days.
    """
    m = re.fullmatch(r"[Tt]\+(\d+)", convention.strip())
    if not m:
        raise ValueError(
            f"quando: invalid convention '{convention}'. Expected 'T+N' (e.g. 'T+2')."
        )
    return add_business_days(parse(value), int(m.group(1)), cal)


def to_cob(value: DateLike, cal: str | None = None) -> datetime:
    """
    Close-of-business date. Returns the date itself if it is a business day,
    otherwise rolls back to the previous business day.
    """
    dt = parse(value)
    return dt if is_business_day(dt, cal) else prev_business_day(dt, cal)


def next_expiry(value: DateLike, contract_type: str) -> datetime:
    """
    Next expiry date after value.
    contract_type: 'monthly' | 'quarterly' | 'weekly'
    """
    dt = parse(value)
    ct = contract_type.lower()
    if ct == "weekly":
        return _next_weekday_after(dt, 4)
    if ct == "monthly":
        return _next_third_friday(dt)
    if ct == "quarterly":
        return _next_quarterly_expiry(dt)
    raise ValueError(
        f"quando: unknown contract_type '{contract_type}'. "
        "Use 'monthly', 'quarterly', or 'weekly'."
    )


def days_to_expiry(value: DateLike, expiry: DateLike, cal: str | None = None) -> int:
    """Business days between value and expiry."""
    return business_days_between(value, expiry, cal)


# ── internal helpers ──────────────────────────────────────────────────────────

def _next_weekday_after(dt: datetime, weekday: int) -> datetime:
    """Strictly next occurrence of weekday (0=Mon, 4=Fri) after dt."""
    days = (weekday - dt.weekday()) % 7 or 7
    d = dt + timedelta(days=days)
    return d.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)


def _third_friday(year: int, month: int) -> datetime:
    from datetime import date
    first = date(year, month, 1)
    offset = (4 - first.weekday()) % 7   # days to first Friday
    return datetime(year, month, 1 + offset + 14, tzinfo=timezone.utc)


def _next_third_friday(dt: datetime) -> datetime:
    d = dt.date()
    tf = _third_friday(d.year, d.month)
    if tf.date() > d:
        return tf
    return _third_friday(d.year + (d.month == 12), d.month % 12 + 1)


def _next_quarterly_expiry(dt: datetime) -> datetime:
    d = dt.date()
    for year in (d.year, d.year + 1):
        for month in (3, 6, 9, 12):
            tf = _third_friday(year, month)
            if tf.date() > d:
                return tf
    return _third_friday(d.year + 1, 3)
