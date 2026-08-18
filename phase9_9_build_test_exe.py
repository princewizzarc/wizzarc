from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SPEC = ROOT / "WizzArc_test.spec"
DIST_APP = ROOT / "dist" / "WizzArc"

print("=" * 72)
print("WizzArc Phase 9.9 - Step 3 Test Build")
print("=" * 72)

for path in [
    ROOT / "main.py",
    ROOT / "assets" / "wizzarc.ico",
    ROOT / "core" / "app_paths.py",
    SPEC,
]:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")

if DIST_APP.exists():
    shutil.rmtree(DIST_APP)

cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--noconfirm",
    "--clean",
    SPEC.name,
]

print()
print("Running:", " ".join(cmd))
print()

result = subprocess.run(cmd, cwd=ROOT)
if result.returncode != 0:
    raise SystemExit(result.returncode)

exe = DIST_APP / "WizzArc.exe"
if not exe.exists():
    raise SystemExit("Build finished but WizzArc.exe was not found.")

print()
print("=" * 72)
print("PHASE 9.9 STEP 3 BUILD: PASS")
print("EXE:", exe)
print(f"EXE size: {exe.stat().st_size / 1024 / 1024:.2f} MB")
print("=" * 72)