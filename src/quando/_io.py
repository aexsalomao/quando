import json

from quando._state import use, get_cal
from quando._calendar import add_holiday, _CUSTOM_ADD


def load_calendar(path: str) -> None:
    """
    Load a custom holiday calendar from a JSON file and set it as active.

    Expected JSON schema:
    {
        "name": "MY_CAL",
        "holidays": [{"date": "YYYY-MM-DD", "name": "Holiday Name"}, ...]
    }
    """
    with open(path) as f:
        data = json.load(f)
    cal_name = data.get("name", "CUSTOM")
    use(cal_name)
    for entry in data.get("holidays", []):
        add_holiday(entry["date"], entry.get("name", "Holiday"), cal=cal_name)


def save_calendar(path: str, cal: str | None = None) -> None:
    """
    Export custom holiday additions for the active (or specified) calendar to JSON.
    Exchange-provided holidays are not written — they are always available at runtime.
    """
    cal_name = get_cal(cal)
    custom = _CUSTOM_ADD.get(cal_name, {})
    data = {
        "name": cal_name,
        "holidays": [
            {"date": d.isoformat(), "name": name}
            for d, name in sorted(custom.items())
        ],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
