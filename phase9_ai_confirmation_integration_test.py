from dataclasses import dataclass

from brain.tool_executor import ToolExecutor


@dataclass
class FakeIntent:
    intent: str
    action: str
    target: str = ""
    parameters: dict = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


def main():

    executed = []

    def fake_executor(command):
        executed.append(command)
        return f"DRY: {command}"

    tool = ToolExecutor(
        fake_executor
    )

    safe = tool.execute(
        FakeIntent(
            intent="desktop_action",
            action="open",
            target="notepad",
        )
    )

    if not safe.success:
        raise AssertionError(safe)

    if executed != ["open notepad"]:
        raise AssertionError(executed)

    print(
        "[PASS] Safe AI action reaches executor"
    )

    before = list(executed)

    dangerous = tool.execute(
        FakeIntent(
            intent="file_action",
            action="delete_file",
            target="test.txt",
        )
    )

    if dangerous.success:
        raise AssertionError(
            "Delete unexpectedly executed."
        )

    if not dangerous.confirmation_required:
        raise AssertionError(
            dangerous
        )

    if executed != before:
        raise AssertionError(
            "Delete reached executor before confirmation."
        )

    print(
        "[PASS] AI delete requires confirmation"
    )

    # Direct command route is also guarded.
    shutdown = tool.execute_command(
        "shutdown"
    )

    if not shutdown.confirmation_required:
        raise AssertionError(
            shutdown
        )

    if executed != before:
        raise AssertionError(
            "Shutdown reached executor before confirmation."
        )

    print(
        "[PASS] AI power command requires confirmation"
    )

    from brain.ai_controller import (
        AIControllerResult,
    )

    result = AIControllerResult(
        success=False,
        route="confirmation",
        confirmation_required=True,
        dangerous_action=(
            dangerous.dangerous_action
        ),
    )

    if (
        result.route != "confirmation"
        or not result.confirmation_required
        or result.dangerous_action is None
    ):
        raise AssertionError(
            result
        )

    print(
        "[PASS] Controller confirmation result supported"
    )

    from pathlib import Path

    main_text = Path(
        "main.py"
    ).read_text(
        encoding="utf-8"
    )

    required_markers = [
        "def handle_ai_confirmation(",
        "def execute_confirmed_dangerous_action(",
        "QMessageBox.question(",
        'source="AI Safety"',
    ]

    for marker in required_markers:
        if marker not in main_text:
            raise AssertionError(
                f"Missing main integration: {marker}"
            )

    print(
        "[PASS] GUI confirmation hook integrated"
    )

    print()
    print(
        "PHASE 9.7 STEP 2: PASS"
    )


if __name__ == "__main__":
    main()