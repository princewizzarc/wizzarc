from pathlib import Path


MAIN_PATH = Path("main.py")


def main():

    if not MAIN_PATH.exists():
        raise AssertionError(
            "main.py was not found."
        )

    text = MAIN_PATH.read_text(
        encoding="utf-8"
    )

    required = [
        "def _shutdown_worker(",
        "def shutdown_background_workers(",
        "def closeEvent(",
        "self.always_on_mic_enabled = False",
        "worker.requestInterruption()",
        "worker.wait(",
    ]

    missing = [
        item
        for item in required
        if item not in text
    ]

    if missing:
        raise AssertionError(
            "Missing safe shutdown pieces: "
            + ", ".join(missing)
        )

    print(
        "[PASS] Phase 9.3 safe shutdown hooks present"
    )

    print(
        "[PASS] Wake auto-restart disabled during shutdown"
    )

    print(
        "[PASS] Worker wait/cleanup logic present"
    )


if __name__ == "__main__":
    main()