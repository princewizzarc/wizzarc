from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"

text = MAIN.read_text(encoding="utf-8")

checks = [
    ("Logo PNG installed", (ROOT / "assets" / "wizzarc_logo.png").exists()),
    ("ICO installed", (ROOT / "assets" / "wizzarc.ico").exists()),
    ("QPixmap imported", "QPixmap" in text),
    ("Packaged LOGO_PATH", 'LOGO_PATH = resource_path("assets", "wizzarc_logo.png")' in text),
    ("Sidebar image logo", "logo_pixmap = QPixmap" in text),
    ("Packaged ICON_PATH", 'ICON_PATH = resource_path("assets", "wizzarc.ico")' in text),
]

print("=" * 72)
print("WizzArc Phase 9.9 - Branding Verification")
print("=" * 72)

failed = 0
for label, ok in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if not ok:
        failed += 1

print("=" * 72)
if failed:
    print(f"PHASE 9.9 BRANDING VERIFY: FAIL ({failed})")
    raise SystemExit(1)

print("PHASE 9.9 BRANDING VERIFY: PASS")
print("=" * 72)