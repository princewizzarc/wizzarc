from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def under(child, parent):
    child = Path(child).resolve()
    parent = Path(parent).resolve()

    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def main():

    print("=" * 72)
    print("WizzArc Phase 9.9 - AppData Storage Verification v2")
    print("=" * 72)
    print()

    from core.app_paths import (
        APP_DATA_DIR,
        DATA_DIR,
        LOG_DIR,
    )

    expected = (
        Path(
            os.environ.get(
                "LOCALAPPDATA",
                str(
                    Path.home()
                    / "AppData"
                    / "Local"
                ),
            )
        )
        / "WizzArc"
    )

    if APP_DATA_DIR.resolve() != expected.resolve():
        raise AssertionError(
            f"Unexpected APP_DATA_DIR: {APP_DATA_DIR}"
        )

    print(
        f"[PASS] APP_DATA_DIR: {APP_DATA_DIR}"
    )

    from core import crash_logger
    from core import activity_logger
    from core import settings_manager
    from brain import memory_manager
    from brain import custom_app_manager

    checks = [
        (
            "Crash log",
            crash_logger.ERROR_LOG_PATH,
            APP_DATA_DIR,
        ),
        (
            "Activity log",
            activity_logger.ACTIVITY_LOG_PATH,
            APP_DATA_DIR,
        ),
        (
            "Memory data directory",
            memory_manager.DEFAULT_DATA_DIR,
            APP_DATA_DIR,
        ),
        (
            "Temporary memory",
            memory_manager.TEMP_HISTORY_FILE,
            APP_DATA_DIR,
        ),
        (
            "Permanent memory",
            memory_manager.PERMANENT_MEMORY_FILE,
            APP_DATA_DIR,
        ),
        (
            "Custom apps",
            custom_app_manager.CUSTOM_APPS_PATH,
            APP_DATA_DIR,
        ),
    ]

    settings_path = getattr(
        settings_manager,
        "SETTINGS_PATH",
        None,
    )

    if settings_path is None:
        manager = getattr(
            settings_manager,
            "SETTINGS_MANAGER",
            None,
        )

        settings_path = getattr(
            manager,
            "storage_path",
            None,
        )

    if settings_path is None:
        raise AssertionError(
            "Could not determine Settings storage path."
        )

    checks.append(
        (
            "Settings",
            settings_path,
            APP_DATA_DIR,
        )
    )

    for label, path, parent in checks:
        if not under(
            path,
            parent,
        ):
            raise AssertionError(
                f"{label} outside AppData: {path}"
            )

        print(
            f"[PASS] {label}: {path}"
        )

    if not DATA_DIR.exists():
        raise AssertionError(
            "DATA_DIR missing."
        )

    if not LOG_DIR.exists():
        raise AssertionError(
            "LOG_DIR missing."
        )

    print()
    print("=" * 72)
    print(
        "PHASE 9.9 STEP 2: PASS"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()