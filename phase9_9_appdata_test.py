from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main():

    print("=" * 72)
    print("WizzArc Phase 9.9 - AppData Storage Verification")
    print("=" * 72)
    print()

    from core.app_paths import (
        APP_DATA_DIR,
        DATA_DIR,
        LOG_DIR,
    )

    expected_root = Path(
        os.environ.get(
            "LOCALAPPDATA",
            str(
                Path.home()
                / "AppData"
                / "Local"
            ),
        )
    ) / "WizzArc"

    if (
        APP_DATA_DIR.resolve()
        != expected_root.resolve()
    ):
        raise AssertionError(
            (
                "Unexpected APP_DATA_DIR: "
                f"{APP_DATA_DIR}"
            )
        )

    print(
        f"[PASS] APP_DATA_DIR = "
        f"{APP_DATA_DIR}"
    )

    if not DATA_DIR.exists():
        raise AssertionError(
            "DATA_DIR does not exist."
        )

    print(
        f"[PASS] DATA_DIR = {DATA_DIR}"
    )

    if not LOG_DIR.exists():
        raise AssertionError(
            "LOG_DIR does not exist."
        )

    print(
        f"[PASS] LOG_DIR = {LOG_DIR}"
    )

    targets = [
        ROOT / "core" / "crash_logger.py",
        ROOT / "core" / "activity_logger.py",
        ROOT / "core" / "settings_manager.py",
        ROOT / "brain" / "memory_manager.py",
        ROOT / "brain" / "custom_app_manager.py",
    ]

    for path in targets:

        text = path.read_text(
            encoding="utf-8",
        )

        if (
            "from core.app_paths "
            "import APP_DATA_DIR"
            not in text
        ):
            raise AssertionError(
                (
                    "Missing AppData import: "
                    f"{path}"
                )
            )

        if (
            " = APP_DATA_DIR"
            not in text
        ):
            raise AssertionError(
                (
                    "Storage root not migrated: "
                    f"{path}"
                )
            )

        print(
            f"[PASS] AppData storage: "
            f"{path.relative_to(ROOT)}"
        )

    from core import crash_logger
    from core import activity_logger

    runtime_paths = [
        (
            "Crash log",
            crash_logger.ERROR_LOG_PATH,
        ),
        (
            "Activity log",
            activity_logger.ACTIVITY_LOG_PATH,
        ),
    ]

    for label, value in runtime_paths:

        value = Path(value)

        try:
            value.resolve().relative_to(
                APP_DATA_DIR.resolve()
            )
        except ValueError:
            raise AssertionError(
                (
                    f"{label} is outside "
                    f"APP_DATA_DIR: {value}"
                )
            )

        print(
            f"[PASS] {label}: {value}"
        )

    print()
    print("=" * 72)
    print(
        "PHASE 9.9 STEP 2: PASS"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()