from __future__ import annotations
from core.app_paths import APP_DATA_DIR

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock


PROJECT_ROOT = APP_DATA_DIR
DATA_DIR = PROJECT_ROOT / "data"
SETTINGS_PATH = DATA_DIR / "settings.json"


DEFAULT_SETTINGS = {
    "wake_phrase": "wizzarc",
    "always_on_mic_default": False,
    "speech_enabled": True,
    "ai_model": "qwen3:4b",
    "start_minimized": False,
}


class SettingsManager:

    def __init__(
        self,
        path=SETTINGS_PATH,
    ):
        self.path = Path(path)
        self._lock = RLock()
        self._settings = deepcopy(
            DEFAULT_SETTINGS
        )

        self.load()

    def _ensure_parent(
        self,
    ):
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _sanitize(
        self,
        data,
    ):
        cleaned = deepcopy(
            DEFAULT_SETTINGS
        )

        if not isinstance(
            data,
            dict,
        ):
            return cleaned

        wake_phrase = str(
            data.get(
                "wake_phrase",
                cleaned["wake_phrase"],
            )
        ).strip().lower()

        if wake_phrase:
            cleaned["wake_phrase"] = (
                wake_phrase
            )

        cleaned[
            "always_on_mic_default"
        ] = bool(
            data.get(
                "always_on_mic_default",
                cleaned[
                    "always_on_mic_default"
                ],
            )
        )

        cleaned[
            "speech_enabled"
        ] = bool(
            data.get(
                "speech_enabled",
                cleaned[
                    "speech_enabled"
                ],
            )
        )

        ai_model = str(
            data.get(
                "ai_model",
                cleaned["ai_model"],
            )
        ).strip()

        if ai_model:
            cleaned["ai_model"] = (
                ai_model
            )

        cleaned[
            "start_minimized"
        ] = bool(
            data.get(
                "start_minimized",
                cleaned[
                    "start_minimized"
                ],
            )
        )

        return cleaned

    def load(
        self,
    ):
        with self._lock:

            self._ensure_parent()

            if not self.path.exists():

                self._settings = deepcopy(
                    DEFAULT_SETTINGS
                )

                self.save()

                return self.all()

            try:

                raw = json.loads(
                    self.path.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                raw = {}

            self._settings = (
                self._sanitize(
                    raw
                )
            )

            # Rewrite file so missing/new keys are added.
            self.save()

            return self.all()

    def save(
        self,
    ):
        with self._lock:

            self._ensure_parent()

            temp_path = self.path.with_suffix(
                self.path.suffix + ".tmp"
            )

            payload = json.dumps(
                self._settings,
                indent=2,
                ensure_ascii=False,
            )

            temp_path.write_text(
                payload,
                encoding="utf-8",
            )

            temp_path.replace(
                self.path
            )

            return str(
                self.path
            )

    def all(
        self,
    ):
        with self._lock:
            return deepcopy(
                self._settings
            )

    def get(
        self,
        key,
        default=None,
    ):
        with self._lock:
            return self._settings.get(
                key,
                default,
            )

    def set(
        self,
        key,
        value,
    ):
        with self._lock:

            if key not in DEFAULT_SETTINGS:
                raise KeyError(
                    f"Unknown setting: {key}"
                )

            candidate = self.all()
            candidate[key] = value

            self._settings = (
                self._sanitize(
                    candidate
                )
            )

            self.save()

            return self._settings[
                key
            ]

    def update(
        self,
        values,
    ):
        if not isinstance(
            values,
            dict,
        ):
            raise TypeError(
                "Settings update must be a dictionary."
            )

        with self._lock:

            unknown = [
                key
                for key in values
                if key not in DEFAULT_SETTINGS
            ]

            if unknown:
                raise KeyError(
                    "Unknown settings: "
                    + ", ".join(
                        unknown
                    )
                )

            candidate = self.all()
            candidate.update(
                values
            )

            self._settings = (
                self._sanitize(
                    candidate
                )
            )

            self.save()

            return self.all()

    def reset(
        self,
    ):
        with self._lock:

            self._settings = deepcopy(
                DEFAULT_SETTINGS
            )

            self.save()

            return self.all()


SETTINGS_MANAGER = SettingsManager()