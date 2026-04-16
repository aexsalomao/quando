from datetime import datetime

from quando._parse import _WEST_EPOCH, DateLike, parse


def to_timestamp(value: DateLike) -> float:
    return parse(value).timestamp()


def to_datetime(value: DateLike) -> datetime:
    return parse(value)


def to_west(value: DateLike) -> int:
    """Excel serial date — days since 1899-12-30 (e.g. 45306 for 2024-01-15)."""
    return (parse(value).date() - _WEST_EPOCH).days


def to_iso(value: DateLike) -> str:
    """ISO 8601: YYYY-MM-DDTHH:MM:SS+00:00."""
    return parse(value).isoformat()


def convert(value: DateLike, to_fmt: str) -> float | datetime | int | str:
    """Universal converter. to_fmt: 'timestamp' | 'datetime' | 'west' | 'iso'."""
    fmt = to_fmt.lower()
    dispatch = {
        "timestamp": to_timestamp,
        "datetime": to_datetime,
        "west": to_west,
        "iso": to_iso,
    }
    if fmt not in dispatch:
        raise ValueError(
            f"quando: unknown format '{to_fmt}'. Use 'timestamp', 'datetime', 'west', or 'iso'."
        )
    return dispatch[fmt](value)  # type: ignore[return-value]


def to_timestamps(values: list[DateLike]) -> list[float]:
    return [to_timestamp(v) for v in values]


def to_datetimes(values: list[DateLike]) -> list[datetime]:
    return [to_datetime(v) for v in values]
