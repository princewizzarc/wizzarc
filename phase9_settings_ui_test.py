from pathlib import Path


def require(
    text,
    marker,
    label,
):
    if marker not in text:
        raise AssertionError(
            f"Missing: {label}"
        )

    print(
        f"[PASS] {label}"
    )


def main():

    settings_page = Path(
        "ui/settings_page.py"
    )

    main_file = Path(
        "main.py"
    )

    if not settings_page.exists():
        raise AssertionError(
            "ui/settings_page.py not found."
        )

    if not main_file.exists():
        raise AssertionError(
            "main.py not found."
        )

    page_text = settings_page.read_text(
        encoding="utf-8"
    )

    main_text = main_file.read_text(
        encoding="utf-8"
    )

    require(
        page_text,
        "class SettingsPage",
        "Settings page class",
    )

    require(
        page_text,
        "settings_saved = Signal(dict)",
        "Settings saved signal",
    )

    require(
        page_text,
        "Save Settings",
        "Save button",
    )

    require(
        page_text,
        "Reset Defaults",
        "Reset defaults button",
    )

    require(
        page_text,
        '"wake_phrase"',
        "Wake phrase field",
    )

    require(
        page_text,
        '"speech_enabled"',
        "Speech preference field",
    )

    require(
        page_text,
        '"always_on_mic_default"',
        "Always-on mic preference field",
    )

    require(
        page_text,
        '"ai_model"',
        "AI model field",
    )

    require(
        page_text,
        '"start_minimized"',
        "Start minimized field",
    )

    require(
        main_text,
        "from ui.settings_page import SettingsPage",
        "Settings page imported by main",
    )

    require(
        main_text,
        "self.settings_page = SettingsPage(",
        "Settings page mounted",
    )

    require(
        main_text,
        "def apply_saved_settings(",
        "Live settings apply hook",
    )

    require(
        main_text,
        "model=self.ai_model",
        "AI model reconnect support",
    )

    print()
    print(
        "PHASE 9.5 STEP 3: PASS"
    )


if __name__ == "__main__":
    main()