from pathlib import Path


def require(text, marker, label):
    if marker not in text:
        raise AssertionError(
            f"Missing: {label}"
        )
    print(
        f"[PASS] {label}"
    )


def main():

    path = Path(
        "main.py"
    )

    if not path.exists():
        raise AssertionError(
            "main.py not found."
        )

    text = path.read_text(
        encoding="utf-8"
    )

    checks = [
        (
            'self.top_page_title = QLabel(',
            "Dynamic top page title",
        ),
        (
            'self.top_page_subtitle = QLabel(',
            "Dynamic top page subtitle",
        ),
        (
            'self.version_badge = QLabel(',
            "Launch build badge",
        ),
        (
            'self.page_names = [',
            "Central page names",
        ),
        (
            'self.page_subtitles = [',
            "Central page subtitles",
        ),
        (
            'self.top_page_title.setText(',
            "Navigation title updates",
        ),
        (
            'self.top_page_subtitle.setText(',
            "Navigation subtitle updates",
        ),
        (
            '#topPageTitle {',
            "Top title styling",
        ),
        (
            '#versionBadge {',
            "Version badge styling",
        ),
        (
            '#menuButton {',
            "Base sidebar styling",
        ),
        (
            'button.setMinimumHeight(',
            "Consistent sidebar hit area",
        ),
    ]

    for marker, label in checks:
        require(
            text,
            marker,
            label,
        )

    print()
    print(
        "PHASE 9.8 STEP 1: PASS"
    )


if __name__ == "__main__":
    main()