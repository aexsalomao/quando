from datetime import datetime, timezone
import calendar as _cal_mod


def start_of_month(value, cal=None) -> datetime:
    from quando._parse import parse
    from quando._checks import is_business_day
    from quando._navigate import next_business_day
    dt = parse(value)
    first = datetime(dt.year, dt.month, 1, tzinfo=timezone.utc)
    return first if is_business_day(first, cal) else next_business_day(first, cal)


def end_of_month(value, cal=None) -> datetime:
    from quando._parse import parse
    from quando._checks import is_business_day
    from quando._navigate import prev_business_day
    dt = parse(value)
    last_day = _cal_mod.monthrange(dt.year, dt.month)[1]
    last = datetime(dt.year, dt.month, last_day, tzinfo=timezone.utc)
    return last if is_business_day(last, cal) else prev_business_day(last, cal)


def start_of_quarter(value, cal=None) -> datetime:
    from quando._parse import parse
    from quando._checks import is_business_day
    from quando._navigate import next_business_day
    dt = parse(value)
    q_start_month = ((dt.month - 1) // 3) * 3 + 1
    first = datetime(dt.year, q_start_month, 1, tzinfo=timezone.utc)
    return first if is_business_day(first, cal) else next_business_day(first, cal)


def end_of_quarter(value, cal=None) -> datetime:
    from quando._parse import parse
    from quando._checks import is_business_day
    from quando._navigate import prev_business_day
    dt = parse(value)
    q_end_month = ((dt.month - 1) // 3) * 3 + 3
    last_day = _cal_mod.monthrange(dt.year, q_end_month)[1]
    last = datetime(dt.year, q_end_month, last_day, tzinfo=timezone.utc)
    return last if is_business_day(last, cal) else prev_business_day(last, cal)
