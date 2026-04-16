from datetime import datetime, date, timezone, timedelta

UTC = timezone.utc
_WEST_EPOCH = date(1899, 12, 30)
# Excel serials for 1970-01-01 through ~2100-12-31
_WEST_MIN = 25569   # 1970-01-01
_WEST_MAX = 73050   # 2099-12-31

_FORMATS = [
    "%Y%m%d",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
]


def parse(value) -> datetime:
    """Normalise any date-like input to a UTC-aware datetime."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=UTC)
    if isinstance(value, int) and _WEST_MIN <= value <= _WEST_MAX:
        d = _WEST_EPOCH + timedelta(days=value)
        return datetime(d.year, d.month, d.day, tzinfo=UTC)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=UTC)
    if isinstance(value, str):
        return _parse_string(value.strip())
    raise TypeError(f"quando: cannot parse type '{type(value).__name__}'")


def _parse_string(s: str) -> datetime:
    # Excel / West serial passed as a string (e.g. "45306")
    if s.isdigit() and _WEST_MIN <= int(s) <= _WEST_MAX:
        d = _WEST_EPOCH + timedelta(days=int(s))
        return datetime(d.year, d.month, d.day, tzinfo=UTC)
    for fmt in _FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=UTC)
        except ValueError:
            pass
    try:
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except ValueError:
        pass
    raise ValueError(f"quando: cannot parse date string '{s}'")
