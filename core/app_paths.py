from __future__ import annotations

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
