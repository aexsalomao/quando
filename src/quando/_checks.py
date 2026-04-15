from datetime import datetime

_WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


def is_weekend(value) -> bool:
    from quando._parse import parse
    return parse(value).weekday() >= 5


def is_holiday(value, cal=None) -> bool:
    from quando._parse import parse
    from quando._state import get_cal
    from quando._calendar import is_holiday_date
    dt = parse(value)
    if dt.weekday() >= 5:
        return False
    return is_holiday_date(dt.date(), get_cal(cal))


def is_business_day(value, cal=None) -> bool:
    from quando._parse import parse
    dt = parse(value)
    return dt.weekday() < 5 and not is_holiday(dt, cal)


def is_expiry_day(value) -> bool:
    """True if date is the third Friday of its month (standard monthly expiry)."""
    from quando._parse import parse
    d = parse(value).date()
    if d.weekday() != 4:          # not a Friday
        return False
    offset = (4 - d.replace(day=1).weekday()) % 7
    return d.day == 1 + offset + 14


def day_of_week(value) -> str:
    from quando._parse import parse
    return _WEEKDAY_NAMES[parse(value).weekday()]
