# Output converters — datetime → timestamp / ISO string / Excel serial / datetime.
# `convert()` is the stringly-dispatched universal form; prefer the typed helpers.

from datetime import datetime
from typing import Literal, overload

from quando._parse import _WEST_EPOCH, DateLike, parse

ConvertFmt = Literal["timestamp", "datetime", "west", "iso"]


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


@overload
def convert(value: DateLike, to_fmt: Literal["timestamp"]) -> float: ...
@overload
def convert(value: DateLike, to_fmt: Literal["datetime"]) -> datetime: ...
@overload
def convert(value: DateLike, to_fmt: Literal["west"]) -> int: ...
@overload
def convert(value: DateLike, to_fmt: Literal["iso"]) -> str: ...
def convert(value: DateLike, to_fmt: str) -> float | datetime | int | str:
    """Universal converter. to_fmt: 'timestamp' | 'datetime' | 'west' | 'iso'."""
    fmt = to_fmt.lower()
    if fmt == "timestamp":
        return to_timestamp(value)
    if fmt == "datetime":
        return to_datetime(value)
    if fmt == "west":
        return to_west(value)
    if fmt == "iso":
        return to_iso(value)
    raise ValueError(
        f"quando: unknown format '{to_fmt}'. Use 'timestamp', 'datetime', 'west', or 'iso'."
    )


def to_timestamps(values: list[DateLike]) -> list[float]:
    return [to_timestamp(v) for v in values]


def to_datetimes(values: list[DateLike]) -> list[datetime]:
    return [to_datetime(v) for v in values]
