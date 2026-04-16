from datetime import datetime, timezone

import pytz

from quando._parse import parse


def shift_tz(value, tz: str) -> datetime:
    """Convert datetime to a different timezone."""
    return parse(value).astimezone(pytz.timezone(tz))


def localize(value, tz: str) -> datetime:
    """Attach a timezone to a naive datetime without shifting the clock."""
    dt = parse(value).replace(tzinfo=None)
    return pytz.timezone(tz).localize(dt)


def strip_tz(value) -> datetime:
    """Remove timezone info; return naive datetime expressed in UTC."""
    dt = parse(value).astimezone(timezone.utc)
    return dt.replace(tzinfo=None)
