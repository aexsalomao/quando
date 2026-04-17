# Global session state: active calendar, verbose flag, as-of date, and calendar lookups.
# The module-level globals back the pyplot-style `q.use()` public API — see CLAUDE.md.

import logging
from datetime import datetime

from quando._parse import DateLike, parse

logger = logging.getLogger(__name__)

_DEFAULT_CAL = "NYSE"
_GLOBAL_CAL: str = _DEFAULT_CAL
_VERBOSE: bool = False
_AS_OF: datetime | None = None

# User-facing name -> exchange_calendars exchange code
CAL_ALIAS: dict[str, str] = {
    "NYSE": "XNYS",
    "EUREX": "XEUR",
    "LSE": "XLON",
    "TSX": "XTSE",
    "ASX": "XASX",
    "HKEX": "XHKG",
    "JPX": "XTKS",
    "CME": "XCME",
}

CAL_TZ: dict[str, str] = {
    "NYSE": "America/New_York",
    "EUREX": "Europe/Berlin",
    "LSE": "Europe/London",
    "TSX": "America/Toronto",
    "ASX": "Australia/Sydney",
    "HKEX": "Asia/Hong_Kong",
    "JPX": "Asia/Tokyo",
    "CME": "America/Chicago",
}


def use(cal: str) -> None:
    global _GLOBAL_CAL
    _GLOBAL_CAL = cal.upper()


def verbose(flag: bool) -> None:
    global _VERBOSE
    _VERBOSE = flag
    logger.setLevel(logging.DEBUG if flag else logging.WARNING)


def as_of(value: DateLike) -> None:
    global _AS_OF
    _AS_OF = parse(value)


def get_cal(cal: str | None = None) -> str:
    if cal is not None:
        return cal.upper()
    return _GLOBAL_CAL


def get_tz(cal: str | None = None) -> str:
    return CAL_TZ.get(get_cal(cal), "UTC")


def get_xcal_name(cal: str | None = None) -> str:
    name = get_cal(cal)
    return CAL_ALIAS.get(name, name)


def get_as_of() -> datetime | None:
    return _AS_OF


def log(msg: str) -> None:
    if _VERBOSE:
        logger.debug(msg)
