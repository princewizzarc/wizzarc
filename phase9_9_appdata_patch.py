from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent

TARGETS = [
    ROOT / "core" / "crash_logger.py",
    ROOT / "core" / "activity_logger.py",
    ROOT / "core" / "settings_manager.py",
    ROOT / "brain" / "memory_manager.py",
    ROOT / "brain" / "custom_app_manager.py",
]


APP_PATHS_SOURCE = r'''from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


APP_NAME = "WizzArc"


def _legacy_project_root():
    return Path(__file__).resolve().parent.parent


def _local_app_data_root():
    value = os.environ.get(
        "LOCALAPPDATA"
    )

    if value:
        return Path(value)

    return (
        Path.home()
        / "AppData"
        / "Local"
    )


APP_DATA_DIR = (
    _local_app_data_root()
    / APP_NAME
)

DATA_DIR = APP_DATA_DIR / "data"
LOG_DIR = APP_DATA_DIR / "logs"

APP_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def resource_path(
    *parts,
):
    if getattr(
        sys,
        "frozen",
        False,
    ):
        base = Path(
            getattr(
                sys,
                "_MEIPASS",
                Path(sys.executable).parent,
            )
        )
    else:
        base = (
            Path(__file__)
            .resolve()
            .parent
            .parent
        )

    return base.joinpath(
        *parts
    )


def _copy_if_missing(
    source,
    destination,
):
    source = Path(source)
    destination = Path(destination)

    if not source.exists():
        return False

    if destination.exists():
        return False

    try:
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if source.is_dir():
            shutil.copytree(
                source,
                destination,
            )
        else:
            shutil.copy2(
                source,
                destination,
            )

        return True

    except Exception:
        return False


def migrate_legacy_storage():
    legacy_root = (
        _legacy_project_root()
    )

    if getattr(
        sys,
        "frozen",
        False,
    ):
        return []

    migrated = []

    for name in (
        "data",
        "logs",
        "memory",
        "config",
    ):
        source = legacy_root / name
        destination = (
            APP_DATA_DIR / name
        )

        if _copy_if_missing(
            source,
            destination,
        ):
            migrated.append(
                str(destination)
            )

    for name in (
        "settings.json",
        "custom_apps.json",
        "permanent_memory.json",
        "temporary_memory.json",
        "automations.json",
        "saved_automations.json",
    ):
        source = legacy_root / name
        destination = (
            APP_DATA_DIR / name
        )

        if _copy_if_missing(
            source,
            destination,
        ):
            migrated.append(
                str(destination)
            )

    return migrated


MIGRATED_PATHS = (
    migrate_legacy_storage()
)
'''


def ensure_import(text):
    marker = (
        "from core.app_paths "
        "import APP_DATA_DIR"
    )

    if marker in text:
        return text

    lines = text.splitlines()

    insert_at = 0

    if (
        lines
        and lines[0].startswith(
            "from __future__"
        )
    ):
        insert_at = 1

    lines.insert(
        insert_at,
        "from core.app_paths import APP_DATA_DIR",
    )

    return "\n".join(lines) + (
        "\n"
        if text.endswith("\n")
        else ""
    )


def patch_storage_root(
    text,
):
    pattern = re.compile(
        r"^(PROJECT_ROOT|BASE_DIR)\s*=\s*"
        r"Path\(__file__\)\.resolve\(\)"
        r"\.parent\.parent\s*$",
        flags=re.MULTILINE,
    )

    matches = list(
        pattern.finditer(
            text
        )
    )

    if not matches:
        already = re.search(
            r"^(PROJECT_ROOT|BASE_DIR)"
            r"\s*=\s*APP_DATA_DIR\s*$",
            text,
            flags=re.MULTILINE,
        )

        if already:
            return text, True

        return text, False

    text = pattern.sub(
        lambda match: (
            f"{match.group(1)} = "
            "APP_DATA_DIR"
        ),
        text,
        count=1,
    )

    return text, True


def main():

    print("=" * 72)
    print("WizzArc Phase 9.9 - AppData Storage Patch")
    print("=" * 72)
    print()

    app_paths = (
        ROOT
        / "core"
        / "app_paths.py"
    )

    app_paths.write_text(
        APP_PATHS_SOURCE,
        encoding="utf-8",
    )

    print(
        "[PASS] Created core/app_paths.py"
    )

    changed = 0
    failed = []

    for path in TARGETS:

        if not path.exists():
            failed.append(
                (
                    path,
                    "file not found",
                )
            )
            print(
                f"[WARN] Missing {path.relative_to(ROOT)}"
            )
            continue

        original = path.read_text(
            encoding="utf-8"
        )

        patched = ensure_import(
            original
        )

        patched, root_ok = (
            patch_storage_root(
                patched
            )
        )

        if not root_ok:
            failed.append(
                (
                    path,
                    (
                        "storage root pattern "
                        "not recognized"
                    ),
                )
            )
            print(
                f"[WARN] Could not patch "
                f"{path.relative_to(ROOT)}"
            )
            continue

        backup = path.with_suffix(
            path.suffix + ".phase9_9_backup"
        )

        if not backup.exists():
            shutil.copy2(
                path,
                backup,
            )

        path.write_text(
            patched,
            encoding="utf-8",
        )

        changed += 1

        print(
            f"[PASS] Patched "
            f"{path.relative_to(ROOT)}"
        )

    print()

    try:
        from core.app_paths import (
            APP_DATA_DIR,
            MIGRATED_PATHS,
        )

        print(
            f"[PASS] Writable app data: "
            f"{APP_DATA_DIR}"
        )

        if MIGRATED_PATHS:
            print(
                "[PASS] Copied legacy data "
                "without deleting originals:"
            )

            for item in MIGRATED_PATHS:
                print(
                    f"       {item}"
                )
        else:
            print(
                "[PASS] No legacy data copy "
                "was needed."
            )

    except Exception as error:
        failed.append(
            (
                app_paths,
                f"migration import failed: {error}",
            )
        )

        print(
            f"[WARN] Migration check failed: "
            f"{error}"
        )

    print()
    print("=" * 72)

    if failed:
        print(
            f"PATCH INCOMPLETE: "
            f"{len(failed)} issue(s)"
        )

        for path, reason in failed:
            try:
                display = path.relative_to(
                    ROOT
                )
            except Exception:
                display = path

            print(
                f" - {display}: {reason}"
            )

        print("=" * 72)
        return 1

    print(
        f"PHASE 9.9 STEP 2 PATCH: PASS "
        f"({changed}/5 storage modules)"
    )
    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )