from __future__ import annotations
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"
ASSETS = ROOT / "assets"

def main():
    print("=" * 72)
    print("WizzArc Phase 9.9 - Branding Integration Patch")
    print("=" * 72)

    logo_src = ROOT / "wizzarc_logo.png"
    icon_src = ROOT / "wizzarc.ico"

    if not MAIN.exists():
        raise FileNotFoundError("main.py missing")
    if not logo_src.exists():
        raise FileNotFoundError("wizzarc_logo.png missing in project root")
    if not icon_src.exists():
        raise FileNotFoundError("wizzarc.ico missing in project root")

    ASSETS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(logo_src, ASSETS / "wizzarc_logo.png")
    shutil.copy2(icon_src, ASSETS / "wizzarc.ico")
    print("[PASS] Branding assets installed")

    text = MAIN.read_text(encoding="utf-8")
    backup = MAIN.with_suffix(".py.phase9_9_branding_backup")
    if not backup.exists():
        shutil.copy2(MAIN, backup)
        print("[PASS] main.py backup created")

    old_gui = "from PySide6.QtGui import QIcon, QColor, QPainter, QPen, QRadialGradient"
    new_gui = "from PySide6.QtGui import QIcon, QColor, QPainter, QPen, QRadialGradient, QPixmap"
    if old_gui in text:
        text = text.replace(old_gui, new_gui, 1)
        print("[PASS] QPixmap import added")

    marker = "from core.action_safety import DangerousAction"
    if "from core.app_paths import resource_path" not in text:
        if marker not in text:
            raise RuntimeError("core import marker not found")
        text = text.replace(
            marker,
            marker + "\nfrom core.app_paths import resource_path",
            1
        )
        print("[PASS] resource_path import added")

    old_paths = 'BASE_DIR = Path(__file__).resolve().parent\nICON_PATH = BASE_DIR / "assets" / "wizzarc.ico"'
    new_paths = 'BASE_DIR = Path(__file__).resolve().parent\nICON_PATH = resource_path("assets", "wizzarc.ico")\nLOGO_PATH = resource_path("assets", "wizzarc_logo.png")'
    if old_paths in text:
        text = text.replace(old_paths, new_paths, 1)
        print("[PASS] Resource paths updated")
    elif 'LOGO_PATH = resource_path("assets", "wizzarc_logo.png")' not in text:
        raise RuntimeError("PATH block not recognized")

    old_logo = """        logo = QLabel(
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
        )"""

    new_logo = """        logo = QLabel()
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
        )"""

    if old_logo in text:
        text = text.replace(old_logo, new_logo, 1)
        print("[PASS] Sidebar logo integrated")
    elif "logo_pixmap = QPixmap" not in text:
        raise RuntimeError("Sidebar logo block not recognized")

    text = text.replace(
        """        sidebar_layout.addSpacing(
            25
        )""",
        """        sidebar_layout.addSpacing(
            18
        )""",
        1
    )

    old_subtitle_css = """            #subtitle {
                color: #7f8da3;
                font-size: 12px;
            }"""
    new_subtitle_css = """            #subtitle {
                color: #8fa7c6;
                font-size: 10px;
                font-weight: 600;
            }"""
    if old_subtitle_css in text:
        text = text.replace(old_subtitle_css, new_subtitle_css, 1)

    MAIN.write_text(text, encoding="utf-8")

    print()
    print("=" * 72)
    print("PHASE 9.9 BRANDING PATCH: PASS")
    print("=" * 72)

if __name__ == "__main__":
    main()