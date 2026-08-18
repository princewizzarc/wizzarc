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
# IMPORTS
# =========================================================

def test_imports():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.intent_engine import IntentEngine
    from brain.ai_router import AIRouter
    from brain.tool_executor import ToolExecutor
    from brain.action_planner import ActionPlanner
    from brain.multi_step_executor import MultiStepExecutor
    from brain.ai_controller import AIController
    from brain.screen_context_provider import ScreenContextProvider
    from brain.screen_ai import ScreenAI
    return "All Phase 7 modules imported."


# =========================================================
# LOCAL BACKEND
# =========================================================

def test_ollama_backend():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama

    backend = connect_ollama(AI_ENGINE)
    status = backend.status()

    if not status.get("ready"):
        raise AssertionError(status)

    return (
        f"Ollama ready with model "
        f"{status.get('model')}."
    )


# =========================================================
# DIRECT AI
# =========================================================

def test_direct_ai():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama

    connect_ollama(AI_ENGINE)

    result = AI_ENGINE.generate(
        "Reply only with: phase7 direct ai working"
    )

    if not result.success:
        raise AssertionError(result.error)

    if "phase7 direct ai working" not in result.text.lower():
        raise AssertionError(
            f"Unexpected AI response: {result.text}"
        )

    return result.text


# =========================================================
# INTENT ENGINE
# =========================================================

def test_desktop_intent():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.intent_engine import IntentEngine

    connect_ollama(AI_ENGINE)

    result = IntentEngine(
        AI_ENGINE
    ).understand(
        "open notepad"
    )

    if result.intent != "desktop_action":
        raise AssertionError(result)

    if result.action != "open":
        raise AssertionError(result)

    if result.target.lower() != "notepad":
        raise AssertionError(result)

    return (
        f"{result.intent} / "
        f"{result.action} / "
        f"{result.target}"
    )


def test_screen_intent():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.intent_engine import IntentEngine

    connect_ollama(AI_ENGINE)

    result = IntentEngine(
        AI_ENGINE
    ).understand(
        "click terminal on screen"
    )

    if result.intent != "screen_action":
        raise AssertionError(result)

    if result.action != "click_text":
        raise AssertionError(result)

    if result.target.lower() != "terminal":
        raise AssertionError(result)

    return (
        f"{result.intent} / "
        f"{result.action} / "
        f"{result.target}"
    )


# =========================================================
# ROUTER
# =========================================================

def test_router_conversation():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_router import AIRouter

    connect_ollama(AI_ENGINE)

    result = AIRouter(
        AI_ENGINE
    ).route(
        "What is Python?"
    )

    if not result.success:
        raise AssertionError(result.error)

    if result.route != "conversation":
        raise AssertionError(result)

    if not result.text.strip():
        raise AssertionError(
            "Conversation text was empty."
        )

    return result.text[:180]


def test_router_action():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_router import AIRouter

    connect_ollama(AI_ENGINE)

    result = AIRouter(
        AI_ENGINE
    ).route(
        "open notepad"
    )

    if not result.success:
        raise AssertionError(result.error)

    if result.route != "action":
        raise AssertionError(result)

    return (
        f"route={result.route}, "
        f"intent={result.intent.intent}"
    )


# =========================================================
# TOOL EXECUTOR (DRY BUILD ONLY)
# =========================================================

def test_tool_mapping():
    from brain.intent_engine import IntentResult
    from brain.tool_executor import ToolExecutor

    executor = ToolExecutor(
        lambda command: command
    )

    intent = IntentResult(
        intent="desktop_action",
        action="open",
        target="notepad",
    )

    command = executor.build_command(
        intent
    )

    if command != "open notepad":
        raise AssertionError(command)

    return command


# =========================================================
# MULTI-STEP PLANNER
# =========================================================

def test_planner():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.action_planner import ActionPlanner

    connect_ollama(AI_ENGINE)

    result = ActionPlanner(
        AI_ENGINE
    ).plan(
        "open chrome and search youtube "
        "for python tutorial"
    )

    if not result.success:
        raise AssertionError(result.error)

    if len(result.steps) < 2:
        raise AssertionError(result)

    first = result.steps[0]
    second = result.steps[1]

    if (
        first.intent != "desktop_action"
        or
        first.action != "open"
    ):
        raise AssertionError(first)

    if second.intent != "browser_action":
        raise AssertionError(second)

    return (
        f"{len(result.steps)} steps planned."
    )


# =========================================================
# MULTI-STEP EXECUTOR (DRY)
# =========================================================

def test_multi_step_executor_dry():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.multi_step_executor import MultiStepExecutor

    connect_ollama(AI_ENGINE)

    executed = []

    def fake_executor(command):
        executed.append(command)
        return f"DRY: {command}"

    result = MultiStepExecutor(
        AI_ENGINE,
        fake_executor
    ).execute(
        "open chrome and search youtube "
        "for python tutorial"
    )

    if not result.success:
        raise AssertionError(result.error)

    if len(executed) < 2:
        raise AssertionError(executed)

    return " | ".join(executed)


# =========================================================
# SCREEN CONTEXT
# =========================================================

def test_screen_context_provider():
    from brain.screen_context_provider import (
        ScreenContextProvider,
    )

    result = (
        ScreenContextProvider()
        .get_context()
    )

    if not result.available:
        raise AssertionError(result.error)

    prompt_context = (
        result.to_prompt_context()
    )

    if "CURRENT SCREEN CONTEXT" not in prompt_context:
        raise AssertionError(
            "Prompt context missing header."
        )

    return (
        f"Screen context available, "
        f"{len(prompt_context)} chars."
    )


# =========================================================
# SCREEN AI
# =========================================================

def test_screen_ai():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.screen_ai import ScreenAI

    connect_ollama(AI_ENGINE)

    result = ScreenAI(
        AI_ENGINE
    ).ask(
        "What can you see on my screen?"
    )

    if not result.success:
        raise AssertionError(result.error)

    if not result.context_used:
        raise AssertionError(
            "Screen context was not used."
        )

    if not result.text.strip():
        raise AssertionError(
            "Screen AI text was empty."
        )

    return result.text[:220]


# =========================================================
# CONTROLLER ROUTES
# =========================================================

def test_controller_conversation():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController

    connect_ollama(AI_ENGINE)

    controller = AIController(
        AI_ENGINE,
        lambda command: f"DRY: {command}",
    )

    result = controller.handle(
        "What is Python?"
    )

    if (
        not result.success
        or
        result.route != "conversation"
    ):
        raise AssertionError(result)

    return result.text[:180]


def test_controller_single_action_dry():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController

    connect_ollama(AI_ENGINE)

    controller = AIController(
        AI_ENGINE,
        lambda command: f"DRY: {command}",
    )

    result = controller.handle(
        "open notepad"
    )

    if (
        not result.success
        or
        result.route != "action"
    ):
        raise AssertionError(result)

    if result.action_command != "open notepad":
        raise AssertionError(result)

    return result.action_command


def test_controller_multi_action_dry():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController

    connect_ollama(AI_ENGINE)

    controller = AIController(
        AI_ENGINE,
        lambda command: f"DRY: {command}",
    )

    result = controller.handle(
        "open chrome and search youtube "
        "for python tutorial"
    )

    if (
        not result.success
        or
        result.route != "multi_action"
    ):
        raise AssertionError(result)

    return result.text[:250]


def test_controller_screen_context():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController

    connect_ollama(AI_ENGINE)

    controller = AIController(
        AI_ENGINE,
        lambda command: f"DRY: {command}",
    )

    result = controller.handle(
        "What can you see on my screen?"
    )

    if (
        not result.success
        or
        result.route != "screen_context"
    ):
        raise AssertionError(result)

    return result.text[:220]


# =========================================================
# OLD COMMAND REGRESSION
# =========================================================

def test_old_command_registry():
    from brain.command_registry import (
        resolve_registered_command,
    )

    commands = [
        "open notepad",
        "show clipboard",
        "show automations",
        "take screenshot",
        "what can you see",
    ]

    missing = []

    for command in commands:
        result = resolve_registered_command(
            command
        )

        if result is None:
            missing.append(command)

    if missing:
        raise AssertionError(
            "Missing old commands: "
            + ", ".join(missing)
        )

    return (
        f"{len(commands)} old commands "
        "still resolve."
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 64)
    print("WizzArc Phase 7 - AI Brain Regression Test")
    print("=" * 64)
    print()

    run_test(
        "Phase 7 imports",
        test_imports
    )

    run_test(
        "Ollama backend",
        test_ollama_backend
    )

    run_test(
        "Direct local AI",
        test_direct_ai
    )

    run_test(
        "Desktop intent",
        test_desktop_intent
    )

    run_test(
        "Screen intent",
        test_screen_intent
    )

    run_test(
        "Conversation router",
        test_router_conversation
    )

    run_test(
        "Action router",
        test_router_action
    )

    run_test(
        "Tool command mapping",
        test_tool_mapping
    )

    run_test(
        "Multi-step planner",
        test_planner
    )

    run_test(
        "Multi-step executor dry run",
        test_multi_step_executor_dry
    )

    run_test(
        "Screen context provider",
        test_screen_context_provider
    )

    run_test(
        "Screen-aware AI",
        test_screen_ai
    )

    run_test(
        "Controller conversation",
        test_controller_conversation
    )

    run_test(
        "Controller single action dry run",
        test_controller_single_action_dry
    )

    run_test(
        "Controller multi-action dry run",
        test_controller_multi_action_dry
    )

    run_test(
        "Controller screen context",
        test_controller_screen_context
    )

    run_test(
        "Older command regression",
        test_old_command_registry
    )

    print()
    print("=" * 64)
    print(
        f"RESULT: {PASSED} passed, "
        f"{FAILED} failed"
    )
    print("=" * 64)

    if FAILED == 0:
        print(
            "PHASE 7 REGRESSION TEST: PASS"
        )
        sys.exit(0)

    print(
        "PHASE 7 REGRESSION TEST: FAIL"
    )
    sys.exit(1)