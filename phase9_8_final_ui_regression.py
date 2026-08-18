from pathlib import Path
import importlib


def check(marker, text, label):
    if marker not in text:
        raise AssertionError(
            f"Missing UI polish marker: {label}"
        )

    print(
        f"[PASS] {label}"
    )


def main():

    print(
        "=" * 68
    )
    print(
        "WizzArc Phase 9.8 - Final UI Polish Regression"
    )
    print(
        "=" * 68
    )
    print()

    main_path = Path(
        "main.py"
    )

    if not main_path.exists():
        raise AssertionError(
            "main.py not found."
        )

    text = main_path.read_text(
        encoding="utf-8"
    )

    checks = [
        (
            "self.top_page_title = QLabel(",
            "Dynamic top page title",
        ),
        (
            "self.top_page_subtitle = QLabel(",
            "Dynamic top page subtitle",
        ),
        (
            "self.version_badge = QLabel(",
            "Launch build badge",
        ),
        (
            "self.page_names = [",
            "Central page metadata",
        ),
        (
            "def refresh_home_status_ui(",
            "Live Home status",
        ),
        (
            "self.home_ai_model_status = QLabel(",
            "Dynamic AI model display",
        ),
        (
            "self.home_ai_mode_badge = QLabel(",
            "Dynamic AI online state",
        ),
        (
            "self.home_mic_status = QLabel(",
            "Dynamic microphone state",
        ),
        (
            "self.command_input.setClearButtonEnabled(",
            "Input clear control",
        ),
        (
            "Enter to send  •  Mic button toggles wake listening",
            "Command usage hint",
        ),
        (
            "def apply_page_focus_state(",
            "Page focus helper",
        ),
        (
            "current_widget.refresh()",
            "Page refresh hook",
        ),
        (
            "#pageTitle {",
            "Consistent page title style",
        ),
        (
            "#pageDescription {",
            "Consistent page description style",
        ),
        (
            "QPushButton:disabled {",
            "Disabled button style",
        ),
        (
            "QToolTip {",
            "Tooltip style",
        ),
        (
            "def handle_ai_confirmation(",
            "Security confirmation UI preserved",
        ),
        (
            "self.activity_page.refresh()",
            "Activity refresh preserved",
        ),
        (
            "self.settings_page = SettingsPage(",
            "Settings page preserved",
        ),
        (
            "self.custom_apps_page = CustomAppsPage()",
            "Custom apps page preserved",
        ),
    ]

    for marker, label in checks:
        check(
            marker,
            text,
            label,
        )

    print()

    # Import/syntax-level UI dependency smoke checks.
    modules = [
        "ui.activity_page",
        "ui.settings_page",
        "ui.custom_apps_page",
        "ui.assistant_page",
    ]

    for module_name in modules:
        importlib.import_module(
            module_name
        )

        print(
            f"[PASS] Import {module_name}"
        )

    print()
    print(
        "=" * 68
    )
    print(
        "PHASE 9.8 FINAL UI REGRESSION: PASS"
    )
    print(
        "=" * 68
    )


if __name__ == "__main__":
    main()