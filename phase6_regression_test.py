import sys
import time
import traceback


# =========================================================
# HELPERS
# =========================================================

PASSED = 0
FAILED = 0


def pass_test(name):
    global PASSED
    PASSED += 1
    print(f"[PASS] {name}")


def fail_test(name, error):
    global FAILED
    FAILED += 1
    print(f"[FAIL] {name}")
    print(f"       {error}")


def run_test(name, func):
    try:
        result = func()
        pass_test(name)

        if result is not None:
            print(f"       {result}")

        return result

    except Exception as error:
        fail_test(
            name,
            f"{type(error).__name__}: {error}"
        )

        traceback.print_exc()

        return None


# =========================================================
# IMPORT TEST
# =========================================================

def test_imports():

    from actions.screen_text_reader import (
        read_screen_text,
        find_text_on_screen,
        get_text_matches_on_screen,
    )

    from actions.screen_understanding import (
        get_screen_summary,
        show_visible_elements,
        show_clickable_elements,
        refresh_screen_snapshot,
        clear_screen_snapshot,
        get_screen_snapshot_status,
        get_screen_change_status,
        get_screen_context_summary,
        get_nearby_text_context,
    )

    from actions.desktop_actions import (
        execute_command,
    )

    return "Core Phase 6 imports loaded."


# =========================================================
# OCR TEST
# =========================================================

def test_ocr():

    from actions.screen_text_reader import (
        read_screen_text,
    )

    text = read_screen_text()

    if not isinstance(
        text,
        str
    ):

        raise AssertionError(
            "OCR result was not text."
        )

    if not text.strip():

        raise AssertionError(
            "OCR returned empty text."
        )

    return (
        f"OCR returned "
        f"{len(text)} characters."
    )


# =========================================================
# SCREEN SUMMARY TEST
# =========================================================

def test_screen_summary():

    from actions.screen_understanding import (
        get_screen_summary,
    )

    result = get_screen_summary()

    if not isinstance(
        result,
        str
    ):

        raise AssertionError(
            "Screen summary was not text."
        )

    if not result.strip():

        raise AssertionError(
            "Screen summary was empty."
        )

    return result[:250]


# =========================================================
# VISIBLE ELEMENTS TEST
# =========================================================

def test_visible_elements():

    from actions.screen_understanding import (
        show_visible_elements,
    )

    result = show_visible_elements(
        10
    )

    if not isinstance(
        result,
        str
    ):

        raise AssertionError(
            "Visible element result "
            "was not text."
        )

    return result[:500]


# =========================================================
# CLICKABLE ELEMENTS TEST
# =========================================================

def test_clickable_elements():

    from actions.screen_understanding import (
        show_clickable_elements,
    )

    result = show_clickable_elements(
        10
    )

    if not isinstance(
        result,
        str
    ):

        raise AssertionError(
            "Clickable element result "
            "was not text."
        )

    return result[:500]


# =========================================================
# SNAPSHOT TEST
# =========================================================

def test_snapshot():

    from actions.screen_understanding import (
        refresh_screen_snapshot,
        get_screen_snapshot_status,
    )

    refresh_result = (
        refresh_screen_snapshot()
    )

    status = (
        get_screen_snapshot_status()
    )

    if "fresh" not in status.lower():

        raise AssertionError(
            f"Snapshot was not fresh: "
            f"{status}"
        )

    return (
        f"{refresh_result} | {status}"
    )


# =========================================================
# SCREEN CHANGE TEST
# =========================================================

def test_screen_change_status():

    from actions.screen_understanding import (
        get_screen_change_status,
    )

    result = (
        get_screen_change_status()
    )

    if not isinstance(
        result,
        str
    ):

        raise AssertionError(
            "Screen change status "
            "was not text."
        )

    return result


# =========================================================
# CONTEXT GROUPING TEST
# =========================================================

def test_context_grouping():

    from actions.screen_understanding import (
        get_screen_context_summary,
    )

    result = (
        get_screen_context_summary()
    )

    if not isinstance(
        result,
        str
    ):

        raise AssertionError(
            "Screen context result "
            "was not text."
        )

    if not result.strip():

        raise AssertionError(
            "Screen context was empty."
        )

    return result[:600]


# =========================================================
# COMMAND ROUTING TEST
# =========================================================

def test_command_handlers():

    from actions.desktop_actions import (
        execute_command,
    )

    commands = [
        "what can you see",
        "show visible elements",
        "show clickable elements",
        "refresh screen snapshot",
        "screen snapshot status",
        "screen change status",
        "show screen context",
    ]

    outputs = []

    for command in commands:

        result = execute_command(
            command
        )

        if result is None:

            raise AssertionError(
                f"Command returned None: "
                f"{command}"
            )

        outputs.append(
            f"{command}: OK"
        )

    return " | ".join(
        outputs
    )


# =========================================================
# REGISTRY TEST
# =========================================================

def test_registry():

    from brain.command_registry import (
        resolve_registered_command,
    )

    commands = [
        "read screen",
        "what can you see",
        "show visible elements",
        "show clickable elements",
        "refresh screen snapshot",
        "clear screen snapshot",
        "screen snapshot status",
        "screen change status",
        "show screen context",
        "context around terminal",
        "click text terminal",
        "click element 1",
    ]

    missing = []

    for command in commands:

        result = (
            resolve_registered_command(
                command
            )
        )

        if result is None:

            missing.append(
                command
            )

    if missing:

        raise AssertionError(
            "Registry missing: "
            + ", ".join(
                missing
            )
        )

    return (
        f"{len(commands)} Phase 6 "
        "commands resolved."
    )


# =========================================================
# OLD COMMAND REGRESSION TEST
# =========================================================

def test_old_commands():

    from brain.command_registry import (
        resolve_registered_command,
    )

    commands = [
        "open chrome",
        "open notepad",
        "show clipboard",
        "show automations",
        "show saved automations",
        "take screenshot",
        "volume up",
    ]

    missing = []

    for command in commands:

        result = (
            resolve_registered_command(
                command
            )
        )

        if result is None:

            missing.append(
                command
            )

    if missing:

        raise AssertionError(
            "Old commands broken/missing: "
            + ", ".join(
                missing
            )
        )

    return (
        f"{len(commands)} older commands "
        "still resolve."
    )


# =========================================================
# CLEAR SNAPSHOT TEST
# =========================================================

def test_clear_snapshot():

    from actions.screen_understanding import (
        clear_screen_snapshot,
        get_screen_snapshot_status,
    )

    clear_result = (
        clear_screen_snapshot()
    )

    status = (
        get_screen_snapshot_status()
    )

    if "no screen snapshot" not in (
        status.lower()
    ):

        raise AssertionError(
            f"Snapshot did not clear: "
            f"{status}"
        )

    return (
        f"{clear_result} | {status}"
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 62)
    print("WizzArc Phase 6 - Screen Vision Regression Test")
    print("=" * 62)
    print()

    run_test(
        "Core imports",
        test_imports
    )

    run_test(
        "Full-screen OCR",
        test_ocr
    )

    run_test(
        "Screen summary",
        test_screen_summary
    )

    run_test(
        "Visible element scan",
        test_visible_elements
    )

    run_test(
        "Clickable element scan",
        test_clickable_elements
    )

    run_test(
        "Snapshot refresh/status",
        test_snapshot
    )

    run_test(
        "Screen-change status",
        test_screen_change_status
    )

    run_test(
        "Screen context grouping",
        test_context_grouping
    )

    run_test(
        "Desktop action handlers",
        test_command_handlers
    )

    run_test(
        "Phase 6 registry",
        test_registry
    )

    run_test(
        "Older command regression",
        test_old_commands
    )

    run_test(
        "Snapshot clear",
        test_clear_snapshot
    )

    print()
    print("=" * 62)
    print(
        f"RESULT: {PASSED} passed, "
        f"{FAILED} failed"
    )
    print("=" * 62)

    if FAILED == 0:

        print(
            "PHASE 6 REGRESSION TEST: PASS"
        )

        sys.exit(
            0
        )

    print(
        "PHASE 6 REGRESSION TEST: FAIL"
    )

    sys.exit(
        1
    )