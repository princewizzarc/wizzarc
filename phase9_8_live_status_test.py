from pathlib import Path

def main():
    text = Path("main.py").read_text(encoding="utf-8")
    checks = [
        ("def refresh_home_status_ui(", "Live Home status helper"),
        ("self.home_ai_model_status = QLabel(", "Dynamic AI model status"),
        ("self.home_ai_mode_badge = QLabel(", "Dynamic AI online badge"),
        ("self.home_mic_status = QLabel(", "Dynamic microphone status"),
        ("self.command_input.setClearButtonEnabled(", "Input clear button"),
        ("self.command_input.setToolTip(", "Input tooltip"),
        ("Enter to send  •  Mic button toggles wake listening", "Keyboard hint"),
        ("#commandHint {", "Hint styling"),
    ]
    for marker, label in checks:
        if marker not in text:
            raise AssertionError(f"Missing: {label}")
        print(f"[PASS] {label}")
    print()
    print("PHASE 9.8 STEP 2: PASS")

if __name__ == "__main__":
    main()