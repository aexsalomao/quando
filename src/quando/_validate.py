from quando._parse import DateLike, parse


def is_valid(value: object) -> bool:
    """Return True if quando can parse the input."""
    try:
        parse(value)  # type: ignore[arg-type]
        return True
    except (TypeError, ValueError):
        return False


def is_same_day(a: DateLike, b: DateLike) -> bool:
    return parse(a).date() == parse(b).date()


def is_before(a: DateLike, b: DateLike) -> bool:
    return parse(a) < parse(b)


def is_after(a: DateLike, b: DateLike) -> bool:
    return parse(a) > parse(b)
