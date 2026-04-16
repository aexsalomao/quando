from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from quando._parse import parse


def shift_tz(value, tz: str) -> datetime:
    """Convert datetime to a different timezone."""
    return parse(value).astimezone(ZoneInfo(tz))


def localize(value, tz: str) -> datetime:
    """Attach a timezone to a naive datetime without shifting the clock."""
    dt = parse(value).replace(tzinfo=None)
    return dt.replace(tzinfo=ZoneInfo(tz))


def strip_tz(value) -> datetime:
    """Remove timezone info; return naive datetime expressed in UTC."""
    dt = parse(value).astimezone(timezone.utc)
    return dt.replace(tzinfo=None)
