from core.crash_logger import (
    ERROR_LOG_PATH,
    install_global_error_handlers,
    log_exception,
)


def main():
    install_global_error_handlers()

    try:
        raise RuntimeError(
            "Phase 9 logger test"
        )
    except Exception as error:
        path = log_exception(
            type(error),
            error,
            error.__traceback__,
            source="Phase 9 Logger Self-Test",
        )

    if not ERROR_LOG_PATH.exists():
        raise AssertionError(
            "Error log file was not created."
        )

    text = ERROR_LOG_PATH.read_text(
        encoding="utf-8"
    )

    if "Phase 9 logger test" not in text:
        raise AssertionError(
            "Test error was not written to log."
        )

    print(
        "[PASS] Global crash logger"
    )
    print(
        f"Log: {path}"
    )


if __name__ == "__main__":
    main()