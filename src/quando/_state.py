import logging
from datetime import datetime

from quando._parse import parse, DateLike

_logger = logging.getLogger("quando")
_handler = logging.StreamHandler()
_logger.addHandler(_handler)
_logger.setLevel(logging.WARNING)

_GLOBAL_CAL: str = "NYSE"
_VERBOSE: bool = False
_AS_OF = None
_CAL_SET: bool = False

# User-facing name -> exchange_calendars exchange code
CAL_ALIAS: dict[str, str] = {
    "NYSE":  "XNYS",
    "EUREX": "XEUR",
    "LSE":   "XLON",
    "TSX":   "XTSE",
    "ASX":   "XASX",
    "HKEX":  "XHKG",
    "JPX":   "XTKS",
    "CME":   "XCME",
}

CAL_TZ: dict[str, str] = {
    "NYSE":  "America/New_York",
    "EUREX": "Europe/Berlin",
    "LSE":   "Europe/London",
    "TSX":   "America/Toronto",
    "ASX":   "Australia/Sydney",
    "HKEX":  "Asia/Hong_Kong",
    "JPX":   "Asia/Tokyo",
    "CME":   "America/Chicago",
}


def use(cal: str) -> None:
    global _GLOBAL_CAL, _CAL_SET
    _GLOBAL_CAL = cal.upper()
    _CAL_SET = True


def verbose(flag: bool) -> None:
    global _VERBOSE
    _VERBOSE = flag
    _logger.setLevel(logging.DEBUG if flag else logging.WARNING)


def as_of(value: DateLike) -> None:
    global _AS_OF
    _AS_OF = parse(value)


def get_cal(cal: str | None = None) -> str:
    global _CAL_SET
    if cal is not None:
        return str(cal).upper()
    if not _CAL_SET:
        _logger.info("quando: no calendar set via q.use(), defaulting to NYSE")
        _CAL_SET = True
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
        _logger.debug(msg)
