from datetime import datetime, timedelta

from quando._parse import parse, DateLike
from quando._checks import is_business_day


def next_business_day(value: DateLike, cal: str | None = None) -> datetime:
    dt = parse(value) + timedelta(days=1)
    while not is_business_day(dt, cal):
        dt += timedelta(days=1)
    return dt


def prev_business_day(value: DateLike, cal: str | None = None) -> datetime:
    dt = parse(value) - timedelta(days=1)
    while not is_business_day(dt, cal):
        dt -= timedelta(days=1)
    return dt


def add_business_days(value: DateLike, n: int, cal: str | None = None) -> datetime:
    dt = parse(value)
    if n == 0:
        return dt
    step = timedelta(days=1 if n > 0 else -1)
    remaining = abs(n)
    while remaining:
        dt += step
        if is_business_day(dt, cal):
            remaining -= 1
    return dt


def snap(value: DateLike, direction: str, cal: str | None = None) -> datetime:
    """
    Snap to nearest business day.
    direction: 'forward' | 'backward' | 'nearest'
    """
    dt = parse(value)
    if is_business_day(dt, cal):
        return dt
    d = direction.lower()
    if d == "forward":
        return next_business_day(dt, cal)
    if d == "backward":
        return prev_business_day(dt, cal)
    if d == "nearest":
        fwd = next_business_day(dt, cal)
        bwd = prev_business_day(dt, cal)
        return bwd if (dt - bwd).days <= (fwd - dt).days else fwd
    raise ValueError(
        f"quando: unknown direction '{direction}'. "
        "Use 'forward', 'backward', or 'nearest'."
    )
