from datetime import datetime


def to_timestamp(value) -> float:
    from quando._parse import parse
    return parse(value).timestamp()


def to_datetime(value) -> datetime:
    from quando._parse import parse
    return parse(value)


def to_west(value) -> str:
    """MM/DD/YYYY — American/Western date format."""
    from quando._parse import parse
    return parse(value).strftime("%m/%d/%Y")


def to_iso(value) -> str:
    """ISO 8601: YYYY-MM-DDTHH:MM:SS+00:00."""
    from quando._parse import parse
    return parse(value).isoformat()


def convert(value, to_fmt: str):
    """Universal converter. to_fmt: 'timestamp' | 'datetime' | 'west' | 'iso'."""
    fmt = to_fmt.lower()
    dispatch = {
        "timestamp": to_timestamp,
        "datetime":  to_datetime,
        "west":      to_west,
        "iso":       to_iso,
    }
    if fmt not in dispatch:
        raise ValueError(
            f"quando: unknown format '{to_fmt}'. "
            "Use 'timestamp', 'datetime', 'west', or 'iso'."
        )
    return dispatch[fmt](value)


def to_timestamps(values) -> list:
    return [to_timestamp(v) for v in values]


def to_datetimes(values) -> list:
    return [to_datetime(v) for v in values]
