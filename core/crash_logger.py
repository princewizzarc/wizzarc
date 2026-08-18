from __future__ import annotations
from core.app_paths import APP_DATA_DIR

import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = APP_DATA_DIR
LOG_DIR = PROJECT_ROOT / "logs"
ERROR_LOG_PATH = LOG_DIR / "wizzarc_errors.log"


def _ensure_log_dir():
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def log_exception(
    error_type,
    error,
    tb,
    *,
    source="Unhandled Exception",
):
    try:
        _ensure_log_dir()

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        trace_text = "".join(
            traceback.format_exception(
                error_type,
                error,
                tb,
            )
        )

        report = (
            "\n"
            + "=" * 72
            + "\n"
            + f"TIME: {timestamp}\n"
            + f"SOURCE: {source}\n"
            + f"ERROR: {error_type.__name__}: {error}\n"
            + "-" * 72
            + "\n"
            + trace_text
            + "=" * 72
            + "\n"
        )

        with ERROR_LOG_PATH.open(
            "a",
            encoding="utf-8",
        ) as log_file:
            log_file.write(
                report
            )

        return str(
            ERROR_LOG_PATH
        )

    except Exception:
        return ""



def log_runtime_error(
    message,
    *,
    source="Runtime Error",
):
    """
    Log a handled runtime failure that does not have an active traceback.
    """

    try:
        _ensure_log_dir()

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        report = (
            "\n"
            + "=" * 72
            + "\n"
            + f"TIME: {timestamp}\n"
            + f"SOURCE: {source}\n"
            + f"ERROR: {message}\n"
            + "=" * 72
            + "\n"
        )

        with ERROR_LOG_PATH.open(
            "a",
            encoding="utf-8",
        ) as log_file:
            log_file.write(
                report
            )

        return str(
            ERROR_LOG_PATH
        )

    except Exception:
        return ""

def global_exception_handler(
    error_type,
    error,
    tb,
):
    if issubclass(
        error_type,
        KeyboardInterrupt,
    ):
        sys.__excepthook__(
            error_type,
            error,
            tb,
        )
        return

    path = log_exception(
        error_type,
        error,
        tb,
        source="Main Thread",
    )

    print(
        "\nWizzArc encountered an unexpected error."
    )

    if path:
        print(
            f"Crash details saved to: {path}"
        )

    sys.__excepthook__(
        error_type,
        error,
        tb,
    )


def threading_exception_handler(
    args,
):
    path = log_exception(
        args.exc_type,
        args.exc_value,
        args.exc_traceback,
        source=(
            f"Background Thread: "
            f"{getattr(args.thread, 'name', 'unknown')}"
        ),
    )

    print(
        "\nWizzArc background task encountered an error."
    )

    if path:
        print(
            f"Error details saved to: {path}"
        )


def install_global_error_handlers():
    sys.excepthook = (
        global_exception_handler
    )

    if hasattr(
        threading,
        "excepthook",
    ):
        threading.excepthook = (
            threading_exception_handler
        )

    return str(
        ERROR_LOG_PATH
    )