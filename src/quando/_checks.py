from quando._parse import parse, DateLike
from quando._state import get_cal
from quando._calendar import is_holiday_date

_WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


def is_weekend(value: DateLike) -> bool:
    return parse(value).weekday() >= 5


def is_holiday(value: DateLike, cal: str | None = None) -> bool:
    dt = parse(value)
    if dt.weekday() >= 5:
        return False
    return is_holiday_date(dt.date(), get_cal(cal))


def is_business_day(value: DateLike, cal: str | None = None) -> bool:
    dt = parse(value)
    return dt.weekday() < 5 and not is_holiday(dt, cal)


def is_expiry_day(value: DateLike) -> bool:
    """True if date is the third Friday of its month (standard monthly expiry)."""
    d = parse(value).date()
    if d.weekday() != 4:          # not a Friday
        return False
    offset = (4 - d.replace(day=1).weekday()) % 7
    return d.day == 1 + offset + 14


def day_of_week(value: DateLike) -> str:
    return _WEEKDAY_NAMES[parse(value).weekday()]
