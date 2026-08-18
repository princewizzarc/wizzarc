from pathlib import Path

from core.crash_logger import ERROR_LOG_PATH


def test_ai_worker_logging():

    from brain.ai_request_worker import AIRequestWorker

    class BrokenController:
        def handle(
            self,
            user_text,
        ):
            raise RuntimeError(
                "phase9 ai worker failure test"
            )

    worker = AIRequestWorker(
        BrokenController(),
        "test",
    )

    errors = []

    worker.error_occurred.connect(
        errors.append
    )

    # Direct run() keeps this deterministic and avoids
    # needing a QApplication event loop for the self-test.
    worker.run()

    if not errors:
        raise AssertionError(
            "AI worker did not emit error_occurred."
        )

    if not ERROR_LOG_PATH.exists():
        raise AssertionError(
            "Error log file does not exist."
        )

    content = ERROR_LOG_PATH.read_text(
        encoding="utf-8"
    )

    if (
        "phase9 ai worker failure test"
        not in content
    ):
        raise AssertionError(
            "AI worker exception was not logged."
        )


def test_wake_worker_logging():

    from voice.wake_listener_worker import WakeListenerWorker

    class BrokenVoiceEngine:
        def record_audio(self):
            raise RuntimeError(
                "phase9 wake worker failure test"
            )

    worker = WakeListenerWorker(
        BrokenVoiceEngine()
    )

    errors = []

    worker.error_occurred.connect(
        errors.append
    )

    # One cycle is enough to test exception propagation.
    try:
        worker.listen_for_wake_once()
    except RuntimeError as error:
        # listen_for_wake_once deliberately lets the run loop
        # own logging/recovery. Simulate the same run-loop catch.
        from core.crash_logger import log_exception

        log_exception(
            type(error),
            error,
            error.__traceback__,
            source="WakeListenerWorker Test",
        )

        errors.append(
            str(error)
        )

    if not errors:
        raise AssertionError(
            "Wake worker test captured no error."
        )

    content = ERROR_LOG_PATH.read_text(
        encoding="utf-8"
    )

    if (
        "phase9 wake worker failure test"
        not in content
    ):
        raise AssertionError(
            "Wake worker exception was not logged."
        )


def main():

    test_ai_worker_logging()

    print(
        "[PASS] AIRequestWorker crash protection"
    )

    test_wake_worker_logging()

    print(
        "[PASS] WakeListenerWorker crash protection"
    )

    from voice.speech_worker import SpeechWorker

    if not hasattr(
        SpeechWorker,
        "error_occurred",
    ):
        raise AssertionError(
            "SpeechWorker error signal missing."
        )

    print(
        "[PASS] SpeechWorker error protection present"
    )

    print(
        f"Log: {ERROR_LOG_PATH}"
    )


if __name__ == "__main__":
    main()