from core.app_paths import APP_DATA_DIR
import json
import os
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

import psutil


# =========================================================
# PATHS
# =========================================================

BASE_DIR = APP_DATA_DIR
DATA_DIR = BASE_DIR / "data"
CUSTOM_APPS_PATH = DATA_DIR / "custom_apps.json"


# =========================================================
# MODEL
# =========================================================

@dataclass
class CustomApp:
    id: str
    name: str
    executable_path: str
    command: str
    aliases: List[str] = field(default_factory=list)
    enabled: bool = True


# =========================================================
# CUSTOM APP MANAGER
# =========================================================

class CustomAppManager:

    def __init__(
        self,
        storage_path=CUSTOM_APPS_PATH,
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.storage_path.exists():
            self._save_raw([])

    # =====================================================
    # STORAGE
    # =====================================================

    def _load_raw(self):

        try:
            data = json.loads(
                self.storage_path.read_text(
                    encoding="utf-8"
                )
            )
        except (
            FileNotFoundError,
            json.JSONDecodeError,
        ):
            return []

        if not isinstance(data, list):
            return []

        return data

    def _save_raw(
        self,
        items,
    ):

        self.storage_path.write_text(
            json.dumps(
                items,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def _normalize(
        self,
        value,
    ):

        return " ".join(
            str(value)
            .lower()
            .strip()
            .split()
        )

    def _to_app(
        self,
        item,
    ):

        aliases = item.get(
            "aliases",
            [],
        )

        if not isinstance(
            aliases,
            list,
        ):
            aliases = []

        return CustomApp(
            id=str(
                item.get(
                    "id",
                    ""
                )
            ),
            name=str(
                item.get(
                    "name",
                    ""
                )
            ),
            executable_path=str(
                item.get(
                    "executable_path",
                    ""
                )
            ),
            command=str(
                item.get(
                    "command",
                    ""
                )
            ),
            aliases=[
                str(alias).strip()
                for alias in aliases
                if str(alias).strip()
            ],
            enabled=bool(
                item.get(
                    "enabled",
                    True,
                )
            ),
        )

    # =====================================================
    # LIST / GET
    # =====================================================

    def list_apps(
        self,
        include_disabled=True,
    ):

        apps = [
            self._to_app(item)
            for item in self._load_raw()
        ]

        if include_disabled:
            return apps

        return [
            app
            for app in apps
            if app.enabled
        ]

    def get_app(
        self,
        app_id,
    ) -> Optional[CustomApp]:

        target_id = str(
            app_id
        ).strip()

        for app in self.list_apps():
            if app.id == target_id:
                return app

        return None

    # =====================================================
    # ADD / UPDATE / DELETE
    # =====================================================

    def add_app(
        self,
        name,
        executable_path,
        command=None,
        aliases=None,
        enabled=True,
    ):

        name = str(
            name
        ).strip()

        executable_path = str(
            executable_path
        ).strip()

        if not name:
            raise ValueError(
                "App name is required."
            )

        if not executable_path:
            raise ValueError(
                "Executable path is required."
            )

        path = Path(
            executable_path
        )

        if not path.exists():
            raise ValueError(
                "Executable path does not exist."
            )

        if path.is_dir():
            raise ValueError(
                "Please select an executable/file, not a folder."
            )

        command = self._normalize(
            command
            or f"open {name}"
        )

        if not command:
            raise ValueError(
                "Command is required."
            )

        aliases = aliases or []

        cleaned_aliases = []

        for alias in aliases:

            normalized = self._normalize(
                alias
            )

            if (
                normalized
                and
                normalized != command
                and
                normalized not in cleaned_aliases
            ):
                cleaned_aliases.append(
                    normalized
                )

        # Do not allow two enabled apps to claim the same
        # trigger because routing would become ambiguous.
        self._ensure_unique_triggers(
            command=command,
            aliases=cleaned_aliases,
            exclude_id=None,
        )

        app = CustomApp(
            id=str(
                uuid.uuid4()
            ),
            name=name,
            executable_path=str(
                path
            ),
            command=command,
            aliases=cleaned_aliases,
            enabled=bool(
                enabled
            ),
        )

        items = self._load_raw()
        items.append(
            asdict(app)
        )
        self._save_raw(
            items
        )

        return app

    def update_app(
        self,
        app_id,
        *,
        name=None,
        executable_path=None,
        command=None,
        aliases=None,
        enabled=None,
    ):

        items = self._load_raw()
        target_id = str(
            app_id
        ).strip()

        found_index = None

        for index, item in enumerate(
            items
        ):
            if str(
                item.get(
                    "id",
                    ""
                )
            ) == target_id:
                found_index = index
                break

        if found_index is None:
            raise ValueError(
                "Custom app was not found."
            )

        current = self._to_app(
            items[
                found_index
            ]
        )

        new_name = (
            current.name
            if name is None
            else str(name).strip()
        )

        new_path = (
            current.executable_path
            if executable_path is None
            else str(executable_path).strip()
        )

        new_command = (
            current.command
            if command is None
            else self._normalize(
                command
            )
        )

        new_aliases = (
            list(
                current.aliases
            )
            if aliases is None
            else [
                self._normalize(alias)
                for alias in aliases
                if self._normalize(alias)
            ]
        )

        new_enabled = (
            current.enabled
            if enabled is None
            else bool(enabled)
        )

        if not new_name:
            raise ValueError(
                "App name is required."
            )

        path = Path(
            new_path
        )

        if (
            not path.exists()
            or
            path.is_dir()
        ):
            raise ValueError(
                "Executable path is invalid."
            )

        if not new_command:
            raise ValueError(
                "Command is required."
            )

        # Remove duplicates and the main command from aliases.
        deduped_aliases = []

        for alias in new_aliases:
            if (
                alias
                and
                alias != new_command
                and
                alias not in deduped_aliases
            ):
                deduped_aliases.append(
                    alias
                )

        self._ensure_unique_triggers(
            command=new_command,
            aliases=deduped_aliases,
            exclude_id=target_id,
        )

        updated = CustomApp(
            id=current.id,
            name=new_name,
            executable_path=str(path),
            command=new_command,
            aliases=deduped_aliases,
            enabled=new_enabled,
        )

        items[
            found_index
        ] = asdict(
            updated
        )

        self._save_raw(
            items
        )

        return updated

    def delete_app(
        self,
        app_id,
    ):

        target_id = str(
            app_id
        ).strip()

        items = self._load_raw()

        kept = [
            item
            for item in items
            if str(
                item.get(
                    "id",
                    ""
                )
            ) != target_id
        ]

        removed = (
            len(kept)
            != len(items)
        )

        if removed:
            self._save_raw(
                kept
            )

        return removed

    def set_enabled(
        self,
        app_id,
        enabled,
    ):

        return self.update_app(
            app_id,
            enabled=bool(
                enabled
            ),
        )

    # =====================================================
    # UNIQUE TRIGGERS
    # =====================================================

    def _ensure_unique_triggers(
        self,
        command,
        aliases,
        exclude_id=None,
    ):

        requested = {
            self._normalize(
                command
            ),
            *[
                self._normalize(
                    alias
                )
                for alias in aliases
            ],
        }

        requested.discard(
            ""
        )

        for app in self.list_apps():

            if (
                exclude_id
                and
                app.id == exclude_id
            ):
                continue

            existing = {
                self._normalize(
                    app.command
                ),
                *[
                    self._normalize(
                        alias
                    )
                    for alias in app.aliases
                ],
            }

            conflict = (
                requested
                & existing
            )

            if conflict:
                trigger = sorted(
                    conflict
                )[0]

                raise ValueError(
                    f"Command/alias '{trigger}' is already used "
                    f"by '{app.name}'."
                )

    # =====================================================
    # RESOLVE USER COMMAND
    # =====================================================

    def resolve_command(
        self,
        user_text,
    ) -> Optional[CustomApp]:

        text = self._normalize(
            user_text
        )

        if not text:
            return None

        for app in self.list_apps(
            include_disabled=False
        ):

            triggers = [
                self._normalize(
                    app.command
                ),
                *[
                    self._normalize(
                        alias
                    )
                    for alias in app.aliases
                ],
            ]

            if text in triggers:
                return app

        return None

    # =====================================================
    # OPEN / CLOSE
    # =====================================================

    def open_app(
        self,
        app_or_command,
    ):

        app = None

        if isinstance(
            app_or_command,
            CustomApp,
        ):
            app = app_or_command

        else:
            app = self.resolve_command(
                app_or_command
            )

            if app is None:
                target = self._normalize(
                    app_or_command
                )

                for candidate in self.list_apps(
                    include_disabled=False
                ):
                    if self._normalize(
                        candidate.name
                    ) == target:
                        app = candidate
                        break

        if app is None:
            return None

        path = Path(
            app.executable_path
        )

        if not path.exists():
            return (
                f"I found {app.name}, but its executable "
                "path no longer exists."
            )

        try:

            os.startfile(
                str(path)
            )

            return (
                f"Opening {app.name}."
            )

        except Exception as error:

            return (
                f"Couldn't open {app.name}: {error}"
            )

    def close_app(
        self,
        app_name,
    ):

        target = self._normalize(
            app_name
        )

        app = None

        for candidate in self.list_apps(
            include_disabled=False
        ):

            names = {
                self._normalize(
                    candidate.name
                ),
                self._normalize(
                    candidate.command
                    .removeprefix(
                        "open "
                    )
                ),
            }

            if target in names:
                app = candidate
                break

        if app is None:
            return None

        executable_name = Path(
            app.executable_path
        ).name.lower()

        terminated = 0

        for process in psutil.process_iter(
            [
                "pid",
                "name",
                "exe",
            ]
        ):

            try:

                process_name = (
                    process.info.get(
                        "name"
                    )
                    or ""
                ).lower()

                process_exe = (
                    process.info.get(
                        "exe"
                    )
                    or ""
                )

                process_exe_name = (
                    Path(
                        process_exe
                    ).name.lower()
                    if process_exe
                    else ""
                )

                if (
                    process_name
                    == executable_name
                    or
                    process_exe_name
                    == executable_name
                ):

                    process.terminate()
                    terminated += 1

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

        if terminated == 0:
            return (
                f"{app.name} does not appear to be running."
            )

        return (
            f"{app.name} closed."
        )


# =========================================================
# GLOBAL INSTANCE
# =========================================================

CUSTOM_APP_MANAGER = CustomAppManager()