from pathlib import Path
from tempfile import TemporaryDirectory

import core.activity_logger as activity_logger


def main():

    original_path = (
        activity_logger.ACTIVITY_LOG_PATH
    )

    with TemporaryDirectory() as temp_dir:

        test_path = (
            Path(temp_dir)
            / "activity.jsonl"
        )

        activity_logger.ACTIVITY_LOG_PATH = (
            test_path
        )

        activity_logger.log_activity(
            "command",
            "open notepad",
            source="Phase 9.6 Test",
            status="success",
        )

        activity_logger.log_activity(
            "ai",
            "What is Python?",
            source="Phase 9.6 Test",
            status="success",
        )

        items = (
            activity_logger.read_activity(
                limit=10
            )
        )

        if len(items) != 2:
            raise AssertionError(
                items
            )

        if (
            items[0].get(
                "message"
            )
            != "What is Python?"
        ):
            raise AssertionError(
                "Newest-first ordering failed."
            )

        print(
            "[PASS] Structured activity logging"
        )

        print(
            "[PASS] Activity read newest-first"
        )

        if not activity_logger.clear_activity():
            raise AssertionError(
                "clear_activity failed."
            )

        if activity_logger.read_activity():
            raise AssertionError(
                "Activity log did not clear."
            )

        print(
            "[PASS] Activity clear"
        )

    activity_logger.ACTIVITY_LOG_PATH = (
        original_path
    )

    print()
    print(
        "PHASE 9.6 STEP 1: PASS"
    )


if __name__ == "__main__":
    main()