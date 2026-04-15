from datetime import datetime, date, timezone

UTC = timezone.utc

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
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=UTC)
    if isinstance(value, str):
        return _parse_string(value.strip())
    raise TypeError(f"quando: cannot parse type '{type(value).__name__}'")


def _parse_string(s: str) -> datetime:
    for fmt in _FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=UTC)
        except ValueError:
            pass
    try:
        import dateutil.parser
        dt = dateutil.parser.parse(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        pass
    raise ValueError(f"quando: cannot parse date string '{s}'")
