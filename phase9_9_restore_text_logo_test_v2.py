from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"

text = MAIN.read_text(encoding="utf-8")

checks = [
    (
        "Text logo restored",
        'logo = QLabel(\n            "WizzArc"\n        )' in text,
    ),
    (
        "Image logo removed from sidebar",
        "logo_pixmap = QPixmap" not in text,
    ),
    (
        "Subtitle restored",
        'subtitle = QLabel(\n            "Desktop AI Assistant"\n        )' in text,
    ),
]

print("=" * 72)
print("WizzArc - Sidebar Text Branding Verification v2")
print("=" * 72)

failed = 0

for label, ok in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if not ok:
        failed += 1

print("=" * 72)

if failed:
    print(f"SIDEBAR TEXT BRANDING VERIFY: FAIL ({failed})")
    raise SystemExit(1)

print("SIDEBAR TEXT BRANDING VERIFY: PASS")
print("=" * 72)