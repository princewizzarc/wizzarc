from __future__ import annotations

import importlib
import importlib.util
import os
from pathlib import Path
import platform
import re
import sys


ROOT = Path(__file__).resolve().parent


def result(label, ok, detail=""):
    status = "PASS" if ok else "WARN"
    print(f"[{status}] {label}")
    if detail:
        print(f"       {detail}")
    return ok


def read_text(path):
    try:
        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return ""


def main():

    print("=" * 72)
    print("WizzArc Phase 9.9 - Release Build Preflight Audit")
    print("=" * 72)
    print()

    print(f"Project: {ROOT}")
    print(f"Python : {sys.version.split()[0]}")
    print(f"OS     : {platform.platform()}")
    print()

    warnings = 0

    # ---------------------------------------------------------
    # 1. Main entry point
    # ---------------------------------------------------------

    main_py = ROOT / "main.py"

    if not result(
        "Main entry point",
        main_py.exists(),
        str(main_py),
    ):
        warnings += 1

    # ---------------------------------------------------------
    # 2. Application icon
    # ---------------------------------------------------------

    icon = (
        ROOT
        / "assets"
        / "wizzarc.ico"
    )

    if not result(
        "Release icon",
        icon.exists(),
        (
            str(icon)
            if icon.exists()
            else "assets/wizzarc.ico is missing."
        ),
    ):
        warnings += 1

    # ---------------------------------------------------------
    # 3. PyInstaller availability
    # ---------------------------------------------------------

    pyinstaller_ready = (
        importlib.util.find_spec(
            "PyInstaller"
        )
        is not None
    )

    if not result(
        "PyInstaller installed",
        pyinstaller_ready,
        (
            "Ready for build."
            if pyinstaller_ready
            else (
                "PyInstaller is not installed "
                "in the active virtual environment."
            )
        ),
    ):
        warnings += 1

    # ---------------------------------------------------------
    # 4. Important application imports
    # ---------------------------------------------------------

    required_modules = [
        "PySide6",
        "psutil",
        "pyautogui",
        "pytesseract",
        "PIL",
        "faster_whisper",
        "pyttsx3",
    ]

    for module_name in required_modules:
        ready = (
            importlib.util.find_spec(
                module_name
            )
            is not None
        )

        if not result(
            f"Dependency: {module_name}",
            ready,
        ):
            warnings += 1

    # ---------------------------------------------------------
    # 5. Internal WizzArc imports
    # ---------------------------------------------------------

    internal_modules = [
        "core.crash_logger",
        "core.settings_manager",
        "core.activity_logger",
        "core.action_safety",
        "brain.ai_controller",
        "brain.ollama_backend",
        "brain.memory_manager",
        "brain.custom_app_manager",
        "voice.voice_engine",
        "ui.assistant_page",
        "ui.settings_page",
        "ui.activity_page",
    ]

    for module_name in internal_modules:
        try:
            importlib.import_module(
                module_name
            )

            result(
                f"Internal import: {module_name}",
                True,
            )

        except Exception as error:
            warnings += 1

            result(
                f"Internal import: {module_name}",
                False,
                str(error),
            )

    # ---------------------------------------------------------
    # 6. Persistent-data path audit
    # ---------------------------------------------------------

    print()
    print("-" * 72)
    print("Persistent-data path audit")
    print("-" * 72)

    scan_files = [
        ROOT / "core" / "crash_logger.py",
        ROOT / "core" / "activity_logger.py",
        ROOT / "core" / "settings_manager.py",
        ROOT / "brain" / "memory_manager.py",
        ROOT / "brain" / "custom_app_manager.py",
        ROOT / "actions" / "automation_manager.py",
    ]

    risky_patterns = (
        "Path(__file__).resolve().parent.parent",
        ' / "logs"',
        ' / "data"',
        ' / "settings.json"',
    )

    risky_files = []

    for path in scan_files:

        if not path.exists():
            continue

        source = read_text(
            path
        )

        hits = [
            pattern
            for pattern in risky_patterns
            if pattern in source
        ]

        if hits:
            risky_files.append(
                path.relative_to(ROOT)
            )

            result(
                f"Bundled writable path: {path.relative_to(ROOT)}",
                False,
                (
                    "Uses project-relative writable storage. "
                    "This should be reviewed before a one-file EXE."
                ),
            )

    if risky_files:
        warnings += len(
            risky_files
        )
    else:
        result(
            "Persistent writable paths",
            True,
            "No obvious project-relative writable paths found.",
        )

    # ---------------------------------------------------------
    # 7. Resource path audit
    # ---------------------------------------------------------

    main_source = read_text(
        main_py
    )

    resource_ok = (
        "wizzarc.ico"
        in main_source
    )

    if not result(
        "Icon referenced by main.py",
        resource_ok,
    ):
        warnings += 1

    # ---------------------------------------------------------
    # 8. Ollama runtime dependency
    # ---------------------------------------------------------

    backend_path = (
        ROOT
        / "brain"
        / "ollama_backend.py"
    )

    backend_source = read_text(
        backend_path
    )

    ollama_external = (
        "127.0.0.1:11434"
        in backend_source
        or "/api/tags"
        in backend_source
    )

    result(
        "Ollama handled as external runtime service",
        ollama_external,
        (
            "WizzArc will not bundle the Ollama model "
            "inside the EXE."
            if ollama_external
            else "Could not verify Ollama runtime handling."
        ),
    )

    if not ollama_external:
        warnings += 1

    # ---------------------------------------------------------
    # 9. Existing release artifacts
    # ---------------------------------------------------------

    build_dir = ROOT / "build"
    dist_dir = ROOT / "dist"

    result(
        "Build directory state",
        True,
        (
            "build/ exists from a previous build."
            if build_dir.exists()
            else "No previous build/ directory."
        ),
    )

    result(
        "Dist directory state",
        True,
        (
            "dist/ exists from a previous build."
            if dist_dir.exists()
            else "No previous dist/ directory."
        ),
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print()
    print("=" * 72)

    if warnings == 0:
        print(
            "PHASE 9.9 STEP 1: READY FOR PACKAGING"
        )
    else:
        print(
            f"PHASE 9.9 STEP 1: AUDIT COMPLETE "
            f"({warnings} warning(s) to review)"
        )

    print("=" * 72)

    # Warnings are expected during this audit, so exit 0.
    # The audit must never block the user from sending us the output.
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )