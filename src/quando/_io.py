# JSON import/export for custom holiday calendars.
# Only custom additions are serialized; exchange holidays stay sourced from exchange_calendars.

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from quando._calendar import _CUSTOM_ADD, add_holiday
from quando._state import get_cal, use


@dataclass(frozen=True)
class _HolidayEntry:
    date: str
    name: str


@dataclass(frozen=True)
class _CalendarFile:
    name: str
    holidays: list[_HolidayEntry]

    @classmethod
    def from_dict(cls, raw: Any) -> "_CalendarFile":
        # raw is deserialized JSON; validate shape explicitly rather than trust it.
        if not isinstance(raw, dict):
            raise ValueError("quando: calendar file must be a JSON object")
        if "name" not in raw:
            raise ValueError("quando: calendar file missing required 'name' field")
        if "holidays" not in raw:
            raise ValueError("quando: calendar file missing required 'holidays' field")
        holidays = raw["holidays"]
        if not isinstance(holidays, list):
            raise ValueError("quando: 'holidays' must be a JSON array")
        entries: list[_HolidayEntry] = []
        for i, entry in enumerate(holidays):
            if not isinstance(entry, dict):
                raise ValueError(f"quando: holiday entry {i} must be a JSON object")
            if "date" not in entry:
                raise ValueError(f"quando: holiday entry {i} missing required 'date' field")
            if "name" not in entry:
                raise ValueError(f"quando: holiday entry {i} missing required 'name' field")
            entries.append(_HolidayEntry(date=str(entry["date"]), name=str(entry["name"])))
        return cls(name=str(raw["name"]), holidays=entries)


def load_calendar(path: str) -> None:
    """
    Load a custom holiday calendar from a JSON file and set it as active.

    Expected JSON schema:
    {
        "name": "MY_CAL",
        "holidays": [{"date": "YYYY-MM-DD", "name": "Holiday Name"}, ...]
    }
    """
    with Path(path).open() as f:
        data = _CalendarFile.from_dict(json.load(f))
    use(data.name)
    for entry in data.holidays:
        add_holiday(entry.date, entry.name, cal=data.name)


def save_calendar(path: str, cal: str | None = None) -> None:
    """
    Export custom holiday additions for the active (or specified) calendar to JSON.
    Exchange-provided holidays are not written — they are always available at runtime.
    """
    cal_name = get_cal(cal)
    custom = _CUSTOM_ADD.get(cal_name, {})
    data = {
        "name": cal_name,
        "holidays": [{"date": d.isoformat(), "name": name} for d, name in sorted(custom.items())],
    }
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)
