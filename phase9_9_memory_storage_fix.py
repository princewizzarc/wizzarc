from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "brain" / "memory_manager.py"


def main():

    print("=" * 72)
    print("WizzArc Phase 9.9 - Memory Storage Fix")
    print("=" * 72)
    print()

    if not TARGET.exists():
        raise FileNotFoundError(
            f"Missing: {TARGET}"
        )

    text = TARGET.read_text(
        encoding="utf-8"
    )

    import_line = (
        "from core.app_paths import DATA_DIR"
    )

    if import_line not in text:
        lines = text.splitlines()
        insert_at = 0

        if (
            lines
            and lines[0].startswith(
                "from __future__"
            )
        ):
            insert_at = 1

        lines.insert(
            insert_at,
            import_line,
        )

        text = "\n".join(lines) + "\n"

    old_block = '''DEFAULT_DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
)'''

    new_block = '''DEFAULT_DATA_DIR = DATA_DIR'''

    if old_block in text:
        text = text.replace(
            old_block,
            new_block,
            1,
        )
    elif (
        "DEFAULT_DATA_DIR = DATA_DIR"
        not in text
    ):
        raise RuntimeError(
            "Current DEFAULT_DATA_DIR block was not recognized."
        )

    backup = TARGET.with_suffix(
        TARGET.suffix + ".phase9_9_backup"
    )

    if not backup.exists():
        shutil.copy2(
            TARGET,
            backup,
        )

    TARGET.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "[PASS] Added DATA_DIR AppData import"
    )
    print(
        "[PASS] memory_manager DEFAULT_DATA_DIR "
        "now uses LocalAppData/WizzArc/data"
    )
    print(
        f"[PASS] Backup: {backup.name}"
    )

    print()
    print("=" * 72)
    print(
        "PHASE 9.9 MEMORY STORAGE FIX: PASS"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()