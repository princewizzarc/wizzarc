from core.crash_logger import (
    ERROR_LOG_PATH,
    log_runtime_error,
)


def main():

    marker = "phase9 handled runtime test"

    path = log_runtime_error(
        marker,
        source="Phase 9.2 Step 2 Test",
    )

    if not ERROR_LOG_PATH.exists():
        raise AssertionError(
            "Runtime log file was not created."
        )

    content = ERROR_LOG_PATH.read_text(
        encoding="utf-8"
    )

    if marker not in content:
        raise AssertionError(
            "Handled runtime error was not logged."
        )

    print(
        "[PASS] Handled runtime error logging"
    )
    print(
        f"Log: {path}"
    )


if __name__ == "__main__":
    main()