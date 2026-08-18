from dataclasses import dataclass
from pathlib import Path

from brain.tool_executor import ToolExecutor
from brain.multi_step_executor import MultiStepExecutor


@dataclass
class FakeIntent:
    intent: str
    action: str
    target: str = ""
    parameters: dict = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class FakeStep:
    number: int
    intent: str
    action: str
    target: str = ""
    parameters: dict = None
    confidence: float = 0.99

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class FakePlan:
    success: bool
    steps: list
    error: str = ""


def main():

    # =====================================================
    # 1. SINGLE SAFE ACTION
    # =====================================================

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

    if executed != [
        "open notepad"
    ]:
        raise AssertionError(executed)

    print(
        "[PASS] Safe single AI action executes"
    )

    # =====================================================
    # 2. SINGLE DELETE BLOCK
    # =====================================================

    before = list(executed)

    delete_result = tool.execute(
        FakeIntent(
            intent="file_action",
            action="delete_file",
            target="phase9_security_test.txt",
        )
    )

    if (
        delete_result.success
        or not delete_result.confirmation_required
    ):
        raise AssertionError(delete_result)

    if executed != before:
        raise AssertionError(
            "Delete reached executor before confirmation."
        )

    print(
        "[PASS] Single AI delete blocked"
    )

    # =====================================================
    # 3. SINGLE POWER BLOCK
    # =====================================================

    shutdown_result = tool.execute_command(
        "shutdown"
    )

    if (
        shutdown_result.success
        or not shutdown_result.confirmation_required
    ):
        raise AssertionError(shutdown_result)

    if executed != before:
        raise AssertionError(
            "Shutdown reached executor before confirmation."
        )

    print(
        "[PASS] Single AI shutdown blocked"
    )

    # =====================================================
    # 4. MULTI-STEP PREFLIGHT
    # =====================================================

    multi_executed = []

    def multi_fake_executor(command):
        multi_executed.append(command)
        return f"DRY: {command}"

    multi = MultiStepExecutor(
        ai_engine=object(),
        command_executor=multi_fake_executor,
    )

    multi.planner.plan = lambda user_text: FakePlan(
        success=True,
        steps=[
            FakeStep(
                number=1,
                intent="desktop_action",
                action="open",
                target="notepad",
            ),
            FakeStep(
                number=2,
                intent="file_action",
                action="delete_file",
                target="phase9_security_test.txt",
            ),
        ],
    )

    multi_result = multi.execute(
        "open notepad and then delete file phase9_security_test.txt"
    )

    if not multi_result.confirmation_required:
        raise AssertionError(multi_result)

    if multi_executed:
        raise AssertionError(
            (
                "Multi-step preflight failed. "
                f"Executed before confirmation: {multi_executed}"
            )
        )

    print(
        "[PASS] Dangerous multi-step blocked before step 1"
    )

    # =====================================================
    # 5. SAFE MULTI-STEP STILL WORKS
    # =====================================================

    multi.planner.plan = lambda user_text: FakePlan(
        success=True,
        steps=[
            FakeStep(
                number=1,
                intent="desktop_action",
                action="open",
                target="notepad",
            ),
            FakeStep(
                number=2,
                intent="desktop_action",
                action="open",
                target="calculator",
            ),
        ],
    )

    safe_multi = multi.execute(
        "open notepad and calculator"
    )

    if not safe_multi.success:
        raise AssertionError(safe_multi)

    if multi_executed != [
        "open notepad",
        "open calculator",
    ]:
        raise AssertionError(multi_executed)

    print(
        "[PASS] Safe multi-step actions still execute"
    )

    # =====================================================
    # 6. GUI + LEGACY CONFIRMATION STATIC CHECK
    # =====================================================

    main_text = Path(
        "main.py"
    ).read_text(
        encoding="utf-8"
    )

    markers = [
        "def handle_ai_confirmation(",
        "def execute_confirmed_dangerous_action(",
        '"Confirm Delete"',
        '"Confirm Shutdown"',
        '"Confirm Restart"',
        "QMessageBox.question(",
    ]

    for marker in markers:
        if marker not in main_text:
            raise AssertionError(
                f"Missing confirmation hook: {marker}"
            )

    print(
        "[PASS] AI + legacy Home confirmations present"
    )

    print()
    print(
        "PHASE 9.7 STEP 3: PASS"
    )


if __name__ == "__main__":
    main()
