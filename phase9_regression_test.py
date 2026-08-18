import sys
import traceback


PASSED = 0
FAILED = 0


def pass_test(name, details=None):
    global PASSED
    PASSED += 1
    print(f"[PASS] {name}")
    if details:
        print(f"       {details}")


def fail_test(name, error):
    global FAILED
    FAILED += 1
    print(f"[FAIL] {name}")
    print(f"       {error}")


def run_test(name, func):
    try:
        result = func()
        pass_test(name, result)
        return result
    except Exception as error:
        fail_test(
            name,
            f"{type(error).__name__}: {error}"
        )
        traceback.print_exc()
        return None


# =========================================================
# CORE IMPORTS
# =========================================================

def test_core_imports():
    from brain.command_router import CommandRouter
    from brain.command_registry import resolve_registered_command
    from brain.custom_app_manager import CUSTOM_APP_MANAGER
    from brain.custom_command_executor import execute_wizzarc_command

    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController
    from brain.memory_manager import MEMORY_MANAGER

    from voice.voice_worker import VoiceWorker
    from voice.speech_worker import SpeechWorker
    from voice.wake_listener_worker import WakeListenerWorker

    from actions.desktop_actions import execute_command
    from actions.screen_understanding import get_screen_snapshot_status

    return "Core Phase 1-8 + Improvement modules imported."


# =========================================================
# COMMAND REGISTRY
# =========================================================

def test_builtin_commands():
    from brain.command_registry import resolve_registered_command

    commands = [
        "open notepad",
        "open chrome",
        "take screenshot",
        "show clipboard",
        "show automations",
        "what can you see",
    ]

    missing = []

    for command in commands:
        if resolve_registered_command(command) is None:
            missing.append(command)

    if missing:
        raise AssertionError(
            "Missing registered commands: "
            + ", ".join(missing)
        )

    return f"{len(commands)} built-in commands resolve."


# =========================================================
# COMMAND ROUTER
# =========================================================

def test_command_router():
    from brain.command_router import CommandRouter

    router = CommandRouter()

    result = router.route(
        "chrome kholo"
    )

    if result != "open chrome":
        raise AssertionError(
            f"Unexpected route: {result!r}"
        )

    return f"'chrome kholo' -> '{result}'"


# =========================================================
# CUSTOM APPS
# =========================================================

def test_custom_app_manager():
    from brain.custom_app_manager import CUSTOM_APP_MANAGER

    apps = CUSTOM_APP_MANAGER.list_apps()

    if not isinstance(apps, list):
        raise AssertionError(
            "list_apps() did not return a list."
        )

    # Non-destructive check only.
    for app in apps:
        if not str(app.name).strip():
            raise AssertionError(
                "A custom app has an empty name."
            )

        if not str(app.command).strip():
            raise AssertionError(
                f"Custom app '{app.name}' has an empty command."
            )

    return f"{len(apps)} custom app(s) loaded."


# =========================================================
# CUSTOM COMMAND BRIDGE
# =========================================================

def test_custom_command_bridge_import():
    from brain.custom_command_executor import (
        execute_wizzarc_command,
    )

    if not callable(
        execute_wizzarc_command
    ):
        raise AssertionError(
            "execute_wizzarc_command is not callable."
        )

    # Do not actually launch/close anything in regression.
    return "Custom command bridge is callable."


# =========================================================
# WAKE PHRASE DETECTION
# =========================================================

def test_wake_phrase_detection():
    from voice.wake_listener_worker import WakeListenerWorker

    # Avoid loading microphone/Whisper. The text matcher itself
    # can be tested with a lightweight dummy voice engine.
    worker = WakeListenerWorker(
        voice_engine=object(),
    )

    positive = [
        "WizzArc",
        "Hey WizzArc",
        "okay wizzarc",
        "hello, WizzArc!",
    ]

    negative = [
        "wizard",
        "open chrome",
        "hello there",
    ]

    for text in positive:
        if not worker._contains_wake_phrase(
            text
        ):
            raise AssertionError(
                f"Wake phrase missed: {text}"
            )

    for text in negative:
        if worker._contains_wake_phrase(
            text
        ):
            raise AssertionError(
                f"False wake detection: {text}"
            )

    return "Wake phrase matcher passed positive/negative checks."


# =========================================================
# MEMORY
# =========================================================

def test_temporary_memory():
    from brain.memory_manager import MEMORY_MANAGER

    marker = "phase9 regression temporary memory"

    MEMORY_MANAGER.clear_temporary()

    MEMORY_MANAGER.add_temporary(
        "user",
        marker,
    )

    items = MEMORY_MANAGER.get_temporary()

    if not items:
        raise AssertionError(
            "Temporary memory returned no items."
        )

    if items[-1].content != marker:
        raise AssertionError(
            f"Unexpected memory item: {items[-1]}"
        )

    MEMORY_MANAGER.clear_temporary()

    return "Temporary memory write/read/cleanup works."


def test_permanent_memory_cycle():
    from brain.memory_manager import MEMORY_MANAGER

    key = "phase9_test_memory"

    try:
        MEMORY_MANAGER.forget(
            key
        )

        MEMORY_MANAGER.remember(
            key,
            "working",
        )

        loaded = MEMORY_MANAGER.get_memory(
            key
        )

        if loaded is None:
            raise AssertionError(
                "Permanent memory was not saved."
            )

        if loaded.value != "working":
            raise AssertionError(
                f"Unexpected value: {loaded.value}"
            )

    finally:
        MEMORY_MANAGER.forget(
            key
        )

    return "Permanent memory save/read/forget works."


# =========================================================
# SCREEN VISION IMPORT / STATE
# =========================================================

def test_screen_vision_state():
    from actions.screen_understanding import (
        get_screen_snapshot_status,
    )

    status = get_screen_snapshot_status()

    if not isinstance(
        status,
        str,
    ):
        raise AssertionError(
            "Screen snapshot status was not text."
        )

    return status[:180]


# =========================================================
# AI BACKEND
# =========================================================

def test_ollama_status():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama

    backend = connect_ollama(
        AI_ENGINE
    )

    status = backend.status()

    if not status.get(
        "ready"
    ):
        raise AssertionError(
            status
        )

    return (
        f"Ollama ready: "
        f"{status.get('model')}"
    )


# =========================================================
# STRUCTURED INTENT
# =========================================================

def test_ai_intent():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.intent_engine import IntentEngine

    connect_ollama(
        AI_ENGINE
    )

    result = IntentEngine(
        AI_ENGINE
    ).understand(
        "open notepad"
    )

    if result.intent != "desktop_action":
        raise AssertionError(
            result
        )

    if result.action != "open":
        raise AssertionError(
            result
        )

    if result.target.lower() != "notepad":
        raise AssertionError(
            result
        )

    return (
        f"{result.intent} / "
        f"{result.action} / "
        f"{result.target}"
    )


# =========================================================
# FINAL CONVERSATION QUALITY
# =========================================================

def test_concise_final_answer():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama

    connect_ollama(
        AI_ENGINE
    )

    result = AI_ENGINE.generate(
        "What is Python? Answer in one short sentence."
    )

    if not result.success:
        raise AssertionError(
            result.error
        )

    text = str(
        result.text
    ).strip()

    if not text:
        raise AssertionError(
            "AI returned an empty answer."
        )

    forbidden = [
        "we are given",
        "the user asks",
        "we need answer",
        "we need to answer",
        "system instruction",
        "hidden context",
        "analysis:",
        "<think>",
        "</think>",
    ]

    lowered = text.lower()

    leaks = [
        phrase
        for phrase in forbidden
        if phrase in lowered
    ]

    if leaks:
        raise AssertionError(
            "Internal reasoning/context leaked: "
            + ", ".join(leaks)
            + f" | response={text!r}"
        )

    # User asked for one short sentence. Keep this intentionally
    # generous so normal punctuation does not cause false failures.
    if len(text) > 450:
        raise AssertionError(
            f"Answer is too verbose ({len(text)} chars): {text}"
        )

    return text


# =========================================================
# AI CONTROLLER DRY ACTION
# =========================================================

def test_ai_controller_action_dry():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController

    connect_ollama(
        AI_ENGINE
    )

    executed = []

    def dry_executor(command):
        executed.append(command)
        return f"DRY: {command}"

    controller = AIController(
        AI_ENGINE,
        dry_executor,
    )

    result = controller.handle(
        "open notepad"
    )

    if not result.success:
        raise AssertionError(
            result
        )

    if result.route != "action":
        raise AssertionError(
            f"Unexpected route: {result}"
        )

    if result.action_command != "open notepad":
        raise AssertionError(
            result
        )

    if "open notepad" not in executed:
        raise AssertionError(
            f"Dry executor did not receive command: {executed}"
        )

    return result.action_command


# =========================================================
# MULTI ACTION DRY TEST
# =========================================================

def test_multi_action_dry():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController

    connect_ollama(
        AI_ENGINE
    )

    executed = []

    def dry_executor(command):
        executed.append(command)
        return f"DRY: {command}"

    controller = AIController(
        AI_ENGINE,
        dry_executor,
    )

    result = controller.handle(
        "open chrome and search youtube for python tutorial"
    )

    if not result.success:
        raise AssertionError(
            result
        )

    if result.route != "multi_action":
        raise AssertionError(
            f"Unexpected route: {result}"
        )

    if len(executed) < 2:
        raise AssertionError(
            f"Expected at least 2 dry actions: {executed}"
        )

    return " | ".join(
        executed
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("WizzArc Phase 9.1 - Final Regression Smoke Test")
    print("=" * 70)
    print()

    tests = [
        (
            "Core imports",
            test_core_imports,
        ),
        (
            "Built-in command registry",
            test_builtin_commands,
        ),
        (
            "Command router",
            test_command_router,
        ),
        (
            "Custom app manager",
            test_custom_app_manager,
        ),
        (
            "Custom command bridge",
            test_custom_command_bridge_import,
        ),
        (
            "Wake phrase detection",
            test_wake_phrase_detection,
        ),
        (
            "Temporary memory",
            test_temporary_memory,
        ),
        (
            "Permanent memory cycle",
            test_permanent_memory_cycle,
        ),
        (
            "Screen vision state",
            test_screen_vision_state,
        ),
        (
            "Ollama status",
            test_ollama_status,
        ),
        (
            "AI structured intent",
            test_ai_intent,
        ),
        (
            "AI concise final answer",
            test_concise_final_answer,
        ),
        (
            "AI controller dry action",
            test_ai_controller_action_dry,
        ),
        (
            "AI multi-action dry run",
            test_multi_action_dry,
        ),
    ]

    for name, func in tests:
        run_test(
            name,
            func,
        )

    print()
    print("=" * 70)
    print("PHASE 9 REGRESSION")
    print(f"Passed: {PASSED}")
    print(f"Failed: {FAILED}")
    print("=" * 70)

    # Final cleanup
    try:
        from brain.memory_manager import MEMORY_MANAGER
        MEMORY_MANAGER.forget(
            "phase9_test_memory"
        )
        MEMORY_MANAGER.clear_temporary()
    except Exception:
        pass

    if FAILED == 0:
        print(
            "PHASE 9.1 REGRESSION: PASS"
        )
        sys.exit(
            0
        )

    print(
        "PHASE 9.1 REGRESSION: FAIL"
    )
    sys.exit(
        1
    )