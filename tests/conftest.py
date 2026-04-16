"""
Reset all quando global state before every test so tests are fully isolated.
"""

import pytest

import quando._calendar as _calendar
import quando._state as _state


@pytest.fixture(autouse=True)
def _reset_quando():
    _state._GLOBAL_CAL = "NYSE"
    _state._VERBOSE = False
    _state._AS_OF = None
    _state._CAL_SET = True  # suppress "defaulting to NYSE" log noise
    _calendar._CUSTOM_ADD.clear()
    _calendar._CUSTOM_REMOVE.clear()
    _calendar._xcal_holidays.cache_clear()
    yield
