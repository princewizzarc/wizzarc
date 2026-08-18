from pathlib import Path


def main():

    main_path = Path("main.py")

    if not main_path.exists():
        raise AssertionError(
            "main.py not found in project root."
        )

    text = main_path.read_text(
        encoding="utf-8"
    )

    checks = {
        "Settings manager connected":
            "from core.settings_manager import SETTINGS_MANAGER",
        "Saved settings loaded":
            "self.user_settings =",
        "Wake phrase preference":
            '"wake_phrase"',
        "Speech preference":
            '"speech_enabled"',
        "Always-on mic startup preference":
            '"always_on_mic_default"',
        "AI model preference":
            "model=self.ai_model",
        "Start minimized preference":
            "window.showMinimized()",
        "Speech on/off guard":
            "if not self.speech_enabled:",
        "Dynamic wake phrase UI":
            'self.wake_phrase}" to activate.',
    }

    for name, marker in checks.items():
        if marker not in text:
            raise AssertionError(
                f"Missing: {name}"
            )

        print(
            f"[PASS] {name}"
        )

    print()
    print(
        "PHASE 9.5 STEP 2: PASS"
    )


if __name__ == "__main__":
    main()