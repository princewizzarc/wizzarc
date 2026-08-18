from pathlib import Path


def main():
    text = Path(
        "main.py"
    ).read_text(
        encoding="utf-8"
    )

    checks = [
        (
            "def apply_page_focus_state(",
            "Page focus helper",
        ),
        (
            "self.apply_page_focus_state(",
            "Page focus integration",
        ),
        (
            "self.command_input.setFocus()",
            "Home input focus restore",
        ),
        (
            "current_widget.refresh()",
            "Refresh-capable page hook",
        ),
        (
            "#pageTitle {",
            "Consistent page title styling",
        ),
        (
            "#pageDescription {",
            "Consistent page description styling",
        ),
        (
            "QPushButton:disabled {",
            "Disabled button styling",
        ),
        (
            "QToolTip {",
            "Tooltip styling",
        ),
        (
            "self.commands_page.setFocus()",
            "Commands page focus",
        ),
    ]

    for marker, label in checks:
        if marker not in text:
            raise AssertionError(
                f"Missing: {label}"
            )
        print(
            f"[PASS] {label}"
        )

    print()
    print(
        "PHASE 9.8 STEP 3: PASS"
    )


if __name__ == "__main__":
    main()