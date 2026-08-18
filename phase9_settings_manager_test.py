from pathlib import Path
from tempfile import TemporaryDirectory

from core.settings_manager import (
    DEFAULT_SETTINGS,
    SettingsManager,
)


def main():

    with TemporaryDirectory() as temp_dir:

        test_path = (
            Path(temp_dir)
            / "settings.json"
        )

        manager = SettingsManager(
            test_path
        )

        if manager.all() != DEFAULT_SETTINGS:
            raise AssertionError(
                "Default settings mismatch."
            )

        if not test_path.exists():
            raise AssertionError(
                "settings.json was not created."
            )

        print(
            "[PASS] Default settings created"
        )

        manager.update(
            {
                "wake_phrase":
                    "hey wizzarc",
                "always_on_mic_default":
                    True,
                "speech_enabled":
                    False,
            }
        )

        reloaded = SettingsManager(
            test_path
        )

        if (
            reloaded.get(
                "wake_phrase"
            )
            != "hey wizzarc"
        ):
            raise AssertionError(
                "Wake phrase did not persist."
            )

        if (
            reloaded.get(
                "always_on_mic_default"
            )
            is not True
        ):
            raise AssertionError(
                "Mic preference did not persist."
            )

        if (
            reloaded.get(
                "speech_enabled"
            )
            is not False
        ):
            raise AssertionError(
                "Speech preference did not persist."
            )

        print(
            "[PASS] Settings persist after reload"
        )

        reloaded.reset()

        if (
            reloaded.all()
            != DEFAULT_SETTINGS
        ):
            raise AssertionError(
                "Reset did not restore defaults."
            )

        print(
            "[PASS] Settings reset works"
        )

    print()
    print(
        "PHASE 9.5 STEP 1: PASS"
    )


if __name__ == "__main__":
    main()