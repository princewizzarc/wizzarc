import json
from pathlib import Path
from datetime import datetime


# =========================================================
# STORE PATH
# =========================================================

STORE_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "automation_store.json"
)


# =========================================================
# ENSURE STORE EXISTS
# =========================================================

def ensure_store():

    STORE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not STORE_PATH.exists():

        STORE_PATH.write_text(
            "[]",
            encoding="utf-8"
        )


# =========================================================
# LOAD RAW DATA
# =========================================================

def load_automation_data():

    ensure_store()

    try:

        text = STORE_PATH.read_text(
            encoding="utf-8"
        )

        data = json.loads(
            text
        )

        if not isinstance(
            data,
            list
        ):
            return []

        return data

    except Exception:

        return []


# =========================================================
# SAVE RAW DATA
# =========================================================

def save_automation_data(
    automations
):

    ensure_store()

    try:

        STORE_PATH.write_text(
            json.dumps(
                automations,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        return True

    except Exception:

        return False


# =========================================================
# SERIALIZE DATETIME
# =========================================================

def datetime_to_text(
    value
):

    if value is None:
        return None

    if isinstance(
        value,
        datetime
    ):

        return value.isoformat()

    return str(
        value
    )


# =========================================================
# DATETIME FROM TEXT
# =========================================================

def text_to_datetime(
    value
):

    if not value:
        return None

    try:

        return datetime.fromisoformat(
            value
        )

    except Exception:

        return None


# =========================================================
# BUILD PERSISTENT RECORD
# =========================================================

def build_persistent_record(
    automation
):

    return {
        "id":
            automation.get(
                "id"
            ),

        "command":
            automation.get(
                "command"
            ),

        "automation_type":
            automation.get(
                "automation_type"
            ),

        "interval_seconds":
            automation.get(
                "interval_seconds"
            ),

        "delay_seconds":
            automation.get(
                "delay_seconds"
            ),

        "max_runs":
            automation.get(
                "max_runs"
            ),

        "run_count":
            automation.get(
                "run_count",
                0
            ),

        "stop_after_seconds":
            automation.get(
                "stop_after_seconds"
            ),

        "created_at":
            datetime_to_text(
                automation.get(
                    "created_at"
                )
            ),

        "run_at":
            datetime_to_text(
                automation.get(
                    "run_at"
                )
            ),

        "stop_at":
            datetime_to_text(
                automation.get(
                    "stop_at"
                )
            ),

        "persistent":
            True,
    }


# =========================================================
# SAVE ONE AUTOMATION
# =========================================================

def save_persistent_automation(
    automation
):

    if not automation:

        return False

    data = load_automation_data()

    record = build_persistent_record(
        automation
    )

    automation_id = record.get(
        "id"
    )

    # Replace same ID if already stored
    new_data = []

    for item in data:

        if (
            item.get(
                "id"
            )
            == automation_id
        ):
            continue

        new_data.append(
            item
        )

    new_data.append(
        record
    )

    return save_automation_data(
        new_data
    )


# =========================================================
# REMOVE ONE AUTOMATION
# =========================================================

def remove_persistent_automation(
    automation_id
):

    data = load_automation_data()

    new_data = [
        item
        for item in data
        if item.get(
            "id"
        )
        != automation_id
    ]

    return save_automation_data(
        new_data
    )


# =========================================================
# CLEAR STORE
# =========================================================

def clear_persistent_automations():

    return save_automation_data(
        []
    )