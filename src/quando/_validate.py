def is_valid(value) -> bool:
    """Return True if quando can parse the input."""
    try:
        from quando._parse import parse
        parse(value)
        return True
    except (TypeError, ValueError):
        return False


def is_same_day(a, b) -> bool:
    from quando._parse import parse
    return parse(a).date() == parse(b).date()


def is_before(a, b) -> bool:
    from quando._parse import parse
    return parse(a) < parse(b)


def is_after(a, b) -> bool:
    from quando._parse import parse
    return parse(a) > parse(b)
