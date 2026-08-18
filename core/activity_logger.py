from __future__ import annotations
from core.app_paths import APP_DATA_DIR

import json
from datetime import datetime
from pathlib import Path
from threading import RLock


PROJECT_ROOT = APP_DATA_DIR
LOG_DIR = PROJECT_ROOT / "logs"
ACTIVITY_LOG_PATH = LOG_DIR / "wizzarc_activity.jsonl"

_LOCK = RLock()


def _ensure_log_dir():
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def log_activity(
    event_type,
    message,
    *,
    source="WizzArc",
    status="info",
    details=None,
):
    """
    Append one structured activity entry to a JSONL log.

    This is separate from crash/error logging.
    """

    try:
        _ensure_log_dir()

        entry = {
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "type": str(
                event_type
            ).strip() or "activity",
            "status": str(
                status
            ).strip() or "info",
            "source": str(
                source
            ).strip() or "WizzArc",
            "message": str(
                message
            ).strip(),
        }

        if details is not None:
            entry["details"] = details

        line = json.dumps(
            entry,
            ensure_ascii=False,
        )

        with _LOCK:
            with ACTIVITY_LOG_PATH.open(
                "a",
                encoding="utf-8",
            ) as log_file:
                log_file.write(
                    line + "\n"
                )

        return entry

    except Exception:
        return {}


def read_activity(
    limit=200,
):
    """
    Read newest activity entries first.
    Invalid/corrupt lines are skipped safely.
    """

    try:
        limit = max(
            1,
            int(limit),
        )

        if not ACTIVITY_LOG_PATH.exists():
            return []

        with _LOCK:
            lines = ACTIVITY_LOG_PATH.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()

        items = []

        for raw_line in reversed(lines):
            raw_line = raw_line.strip()

            if not raw_line:
                continue

            try:
                item = json.loads(
                    raw_line
                )
            except Exception:
                continue

            if isinstance(
                item,
                dict,
            ):
                items.append(
                    item
                )

            if len(items) >= limit:
                break

        return items

    except Exception:
        return []


def clear_activity():
    try:
        _ensure_log_dir()

        with _LOCK:
            ACTIVITY_LOG_PATH.write_text(
                "",
                encoding="utf-8",
            )

        return True

    except Exception:
        return False