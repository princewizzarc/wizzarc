from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "dist" / "WizzArc"
EXE = APP / "WizzArc.exe"

print("=" * 72)
print("WizzArc Phase 9.9 - Step 3 Build Verification")
print("=" * 72)
print()

checks = [
    ("WizzArc.exe", EXE.exists()),
    (
        "Bundled assets",
        (APP / "_internal" / "assets").exists()
        or (APP / "assets").exists(),
    ),
]

failed = 0
for label, ok in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if not ok:
        failed += 1

if EXE.exists():
    print(f"[PASS] EXE size: {EXE.stat().st_size / 1024 / 1024:.2f} MB")

print()
print("=" * 72)
if failed:
    print(f"PHASE 9.9 STEP 3 VERIFY: FAIL ({failed} issue(s))")
    raise SystemExit(1)

print("PHASE 9.9 STEP 3 VERIFY: PASS")
print("=" * 72)