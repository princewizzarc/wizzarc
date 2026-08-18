from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST_APP = ROOT / "dist" / "WizzArc"
EXE = DIST_APP / "WizzArc.exe"


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if detail:
        print(f"       {detail}")
    return bool(condition)


def main():

    print("=" * 72)
    print("WizzArc Phase 9.10 - Final Launch Readiness Test")
    print("=" * 72)
    print()

    passed = 0
    failed = 0

    def record(label, condition, detail=""):
        nonlocal passed, failed
        ok = check(label, condition, detail)
        if ok:
            passed += 1
        else:
            failed += 1
        return ok

    # ---------------------------------------------------------
    # RELEASE FILES
    # ---------------------------------------------------------

    record(
        "Release EXE exists",
        EXE.exists(),
        str(EXE),
    )

    record(
        "Bundled assets exist",
        (
            (DIST_APP / "_internal" / "assets").exists()
            or
            (DIST_APP / "assets").exists()
        ),
        str(DIST_APP),
    )

    # ---------------------------------------------------------
    # PERSISTENT STORAGE
    # ---------------------------------------------------------

    from core.app_paths import (
        APP_DATA_DIR,
        DATA_DIR,
        LOG_DIR,
    )

    expected_appdata = (
        Path(
            os.environ.get(
                "LOCALAPPDATA",
                str(Path.home() / "AppData" / "Local"),
            )
        )
        / "WizzArc"
    )

    record(
        "AppData root",
        APP_DATA_DIR.resolve() == expected_appdata.resolve(),
        str(APP_DATA_DIR),
    )

    record(
        "Persistent data directory",
        DATA_DIR.exists(),
        str(DATA_DIR),
    )

    record(
        "Persistent log directory",
        LOG_DIR.exists(),
        str(LOG_DIR),
    )

    # ---------------------------------------------------------
    # CORE IMPORTS
    # ---------------------------------------------------------

    try:
        from core.settings_manager import SETTINGS_MANAGER
        from core.activity_logger import log_activity
        from core.action_safety import classify_dangerous_action
        from brain.memory_manager import MEMORY_MANAGER
        from brain.custom_app_manager import CUSTOM_APP_MANAGER
        from brain.ai_controller import AIController
        from voice.voice_engine import VoiceEngine

        record(
            "Final core imports",
            True,
            "Settings, activity, safety, memory, custom apps, AI and voice imported.",
        )
    except Exception as error:
        record(
            "Final core imports",
            False,
            str(error),
        )
        print()
        print("=" * 72)
        print(
            f"PHASE 9.10 FINAL READINESS: FAIL "
            f"({failed} issue(s))"
        )
        print("=" * 72)
        raise SystemExit(1)

    # ---------------------------------------------------------
    # SETTINGS READ
    # ---------------------------------------------------------

    try:
        settings = SETTINGS_MANAGER.all()

        required_keys = {
            "wake_phrase",
            "always_on_mic_default",
            "speech_enabled",
            "ai_model",
            "start_minimized",
        }

        record(
            "Settings readable",
            isinstance(settings, dict),
            f"{len(settings)} setting(s) loaded.",
        )

        record(
            "Required settings present",
            required_keys.issubset(settings.keys()),
            ", ".join(sorted(required_keys)),
        )

    except Exception as error:
        record(
            "Settings readable",
            False,
            str(error),
        )

    # ---------------------------------------------------------
    # MEMORY READ
    # ---------------------------------------------------------

    try:
        MEMORY_MANAGER.cleanup_temporary_history()

        record(
            "Memory manager operational",
            True,
            "Temporary-history cleanup completed safely.",
        )
    except Exception as error:
        record(
            "Memory manager operational",
            False,
            str(error),
        )

    # ---------------------------------------------------------
    # CUSTOM APPS READ
    # ---------------------------------------------------------

    try:
        apps = CUSTOM_APP_MANAGER.list_apps()

        record(
            "Custom apps storage readable",
            isinstance(apps, list),
            f"{len(apps)} custom app(s) loaded.",
        )
    except Exception as error:
        record(
            "Custom apps storage readable",
            False,
            str(error),
        )

    # ---------------------------------------------------------
    # ACTIVITY LOG WRITE
    # ---------------------------------------------------------

    try:
        log_activity(
            "phase9_10_test",
            {
                "status": "final_readiness",
                "safe_test": True,
            },
        )

        record(
            "Activity logging operational",
            True,
            "Safe final-readiness event written.",
        )
    except Exception as error:
        record(
            "Activity logging operational",
            False,
            str(error),
        )

    # ---------------------------------------------------------
    # SECURITY CLASSIFICATION - NO EXECUTION
    # ---------------------------------------------------------

    try:
        shutdown_action = classify_dangerous_action(
            "shutdown"
        )

        delete_action = classify_dangerous_action(
            "delete file C:\\WizzArc_Test\\sample.txt"
        )

        record(
            "Shutdown safety classification",
            shutdown_action is not None,
            "Classification only; no shutdown executed.",
        )

        record(
            "Delete safety classification",
            delete_action is not None,
            "Classification only; no file deletion executed.",
        )

    except Exception as error:
        record(
            "Dangerous-action safety classification",
            False,
            str(error),
        )

    # ---------------------------------------------------------
    # FINAL SUMMARY
    # ---------------------------------------------------------

    print()
    print("=" * 72)
    print("PHASE 9.10 FINAL READINESS")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 72)

    if failed:
        print("PHASE 9.10 FINAL READINESS: FAIL")
        raise SystemExit(1)

    print("PHASE 9.10 FINAL READINESS: PASS")
    print()
    print(
        "Next: manually launch dist\\WizzArc\\WizzArc.exe "
        "and perform the final visual/runtime checklist."
    )
    print("=" * 72)


if __name__ == "__main__":
    main()