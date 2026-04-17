# Boolean validation predicates — parseability and date comparisons.

from typing import Any

from quando._parse import DateLike, parse


def is_valid(value: Any) -> bool:
    """Return True if quando can parse the input. Accepts anything by design."""
    try:
        parse(value)
        return True
    except (TypeError, ValueError):
        return False


def is_same_day(a: DateLike, b: DateLike) -> bool:
    return parse(a).date() == parse(b).date()


def is_before(a: DateLike, b: DateLike) -> bool:
    return parse(a) < parse(b)


def is_after(a: DateLike, b: DateLike) -> bool:
    return parse(a) > parse(b)
