from datetime import datetime
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")

def day_key_london() -> str:
    return datetime.now(LONDON).date().isoformat()  # e.g. "2026-02-22"
