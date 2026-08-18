from __future__ import annotations

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"


def main():

    print("=" * 72)
    print("WizzArc - Restore Sidebar Text Branding")
    print("=" * 72)
    print()

    if not MAIN.exists():
        raise FileNotFoundError(
            f"Missing main.py: {MAIN}"
        )

    text = MAIN.read_text(
        encoding="utf-8"
    )

    backup = MAIN.with_suffix(
        ".py.phase9_9_before_text_restore"
    )

    if not backup.exists():
        shutil.copy2(
            MAIN,
            backup,
        )
        print(
            f"[PASS] Backup created: {backup.name}"
        )

    image_block = '''        logo = QLabel()
        logo.setObjectName(
            "logo"
        )
        logo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        logo.setFixedHeight(
            72
        )

        if LOGO_PATH.exists():
            logo_pixmap = QPixmap(
                str(LOGO_PATH)
            )
            if not logo_pixmap.isNull():
                logo.setPixmap(
                    logo_pixmap.scaled(
                        190,
                        72,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
        else:
            logo.setText(
                "WizzArc"
            )

        sidebar_layout.addWidget(
            logo
        )

        subtitle = QLabel(
            "DESKTOP AI ASSISTANT"
        )
        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )'''

    text_block = '''        logo = QLabel(
            "WizzArc"
        )

        logo.setObjectName(
            "logo"
        )

        sidebar_layout.addWidget(
            logo
        )

        subtitle = QLabel(
            "Desktop AI Assistant"
        )'''

    if image_block in text:
        text = text.replace(
            image_block,
            text_block,
            1,
        )
        print(
            "[PASS] Sidebar image logo replaced with text logo."
        )

    elif text_block in text:
        print(
            "[PASS] Sidebar is already using text branding."
        )

    else:
        raise RuntimeError(
            "Current sidebar branding block was not recognized."
        )

    text = text.replace(
        '''        sidebar_layout.addSpacing(
            18
        )''',
        '''        sidebar_layout.addSpacing(
            25
        )''',
        1,
    )

    text = text.replace(
        '''            #subtitle {
                color: #8fa7c6;
                font-size: 10px;
                font-weight: 600;
            }''',
        '''            #subtitle {
                color: #7f8da3;
                font-size: 12px;
            }''',
        1,
    )

    MAIN.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "[PASS] Original subtitle styling restored."
    )
    print(
        "[PASS] Original sidebar spacing restored."
    )

    print()
    print("=" * 72)
    print(
        "SIDEBAR TEXT BRANDING RESTORE: PASS"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()