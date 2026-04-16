from quando._parse import parse


def is_valid(value) -> bool:
    """Return True if quando can parse the input."""
    try:
        parse(value)
        return True
    except (TypeError, ValueError):
        return False


def is_same_day(a, b) -> bool:
    return parse(a).date() == parse(b).date()


def is_before(a, b) -> bool:
    return parse(a) < parse(b)


def is_after(a, b) -> bool:
    return parse(a) > parse(b)
