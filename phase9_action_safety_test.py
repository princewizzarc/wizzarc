from core.action_safety import (
    ConfirmationRequired,
    classify_dangerous_action,
    execute_guarded,
    requires_confirmation,
)


def main():

    dangerous = [
        ("shutdown", "shutdown"),
        ("restart", "restart"),
        ("delete file test.txt", "delete"),
        ("delete folder old project", "delete"),
        ("remove notes.txt", "delete"),
    ]

    for command, expected_kind in dangerous:

        action = classify_dangerous_action(
            command
        )

        if action is None:
            raise AssertionError(
                f"Not detected: {command}"
            )

        if action.kind != expected_kind:
            raise AssertionError(
                (
                    command,
                    action.kind,
                    expected_kind,
                )
            )

    print(
        "[PASS] Dangerous actions detected"
    )

    safe_commands = [
        "open notepad",
        "close chrome",
        "volume up",
        "take screenshot",
        "search google for python",
    ]

    for command in safe_commands:
        if requires_confirmation(
            command
        ):
            raise AssertionError(
                f"False positive: {command}"
            )

    print(
        "[PASS] Normal actions remain allowed"
    )

    executed = []

    def fake_executor(
        command,
    ):
        executed.append(
            command
        )
        return (
            f"DRY: {command}"
        )

    result = execute_guarded(
        "open notepad",
        fake_executor,
    )

    if result != "DRY: open notepad":
        raise AssertionError(
            result
        )

    if executed != [
        "open notepad"
    ]:
        raise AssertionError(
            executed
        )

    print(
        "[PASS] Safe command reaches executor"
    )

    before = list(
        executed
    )

    try:
        execute_guarded(
            "delete file secret.txt",
            fake_executor,
        )

    except ConfirmationRequired as error:

        if error.action.kind != "delete":
            raise AssertionError(
                error.action
            )

    else:
        raise AssertionError(
            "Dangerous command was not blocked."
        )

    if executed != before:
        raise AssertionError(
            "Dangerous command reached executor."
        )

    print(
        "[PASS] Dangerous command blocked before execution"
    )

    try:
        execute_guarded(
            "shutdown",
            fake_executor,
        )

    except ConfirmationRequired as error:

        if error.action.kind != "shutdown":
            raise AssertionError(
                error.action
            )

    else:
        raise AssertionError(
            "Shutdown was not blocked."
        )

    if executed != before:
        raise AssertionError(
            "Shutdown reached executor."
        )

    print(
        "[PASS] Power action blocked before execution"
    )

    print()
    print(
        "PHASE 9.7 STEP 1: PASS"
    )


if __name__ == "__main__":
    main()