import json
from datetime import datetime, timedelta
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent / "state.json"


def _load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)

    except Exception as e:
        print(f"Error occurred: {e}")
        return {}


def _save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


def should_notify_login_alert(cooldown_hours=6):
    state = _load_state()
    last = state.get("last_login_alert")

    if not last:
        return True

    last_time = datetime.strptime(last, "%Y-%m-%d %H:%M")
    return datetime.now() - last_time > timedelta(hours=cooldown_hours)


def mark_login_alert_sent():
    state = _load_state()
    state["last_login_alert"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    _save_state(state)


def reset_login_alert():
    state = _load_state()
    state.pop("last_login_alert", None)
    _save_state(state)
