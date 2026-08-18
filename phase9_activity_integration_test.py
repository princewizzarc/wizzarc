from pathlib import Path

def check(text, marker, label):
    if marker not in text:
        raise AssertionError(f"Missing: {label}")
    print(f"[PASS] {label}")

def main():
    main_path = Path("main.py")
    if not main_path.exists():
        raise AssertionError("main.py not found.")

    text = main_path.read_text(encoding="utf-8")

    checks = [
        ("from core.activity_logger import log_activity", "Activity logger imported"),
        ("from ui.activity_page import ActivityPage", "Activity page imported"),
        ("self.activity_page = ActivityPage(", "Activity page mounted"),
        ('"voice_input"', "Voice input logging"),
        ('"ai_request"', "AI request logging"),
        ('"ai_result"', "AI result logging"),
        ('"command"', "Command logging"),
        ('"system_action"', "System action logging"),
        ('"desktop_action"', "Desktop action logging"),
        ('"power_action"', "Power action logging"),
        ("self.activity_page.refresh()", "Activity auto-refresh"),
    ]

    for marker, label in checks:
        check(text, marker, label)

    print()
    print("PHASE 9.6 STEP 2: PASS")

if __name__ == "__main__":
    main()