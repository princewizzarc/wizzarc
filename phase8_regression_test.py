import sys
import traceback
from datetime import timedelta

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
    from brain.memory_manager import MEMORY_MANAGER
    from brain.action_context_resolver import ActionContextResolver
    from brain.ai_controller import AIController
    return "Phase 8 modules imported."


# =========================================================
# TEMPORARY MEMORY
# =========================================================

def test_temporary_memory():
    from brain.memory_manager import MEMORY_MANAGER

    MEMORY_MANAGER.clear_temporary()

    MEMORY_MANAGER.add_temporary(
        "user",
        "hello memory"
    )

    items = MEMORY_MANAGER.get_temporary()

    if not items:
        raise AssertionError(
            "Temporary memory was empty."
        )

    if items[-1].content != "hello memory":
        raise AssertionError(items[-1])

    return "Temporary history write/read works."


def test_recent_context():
    from brain.memory_manager import MEMORY_MANAGER

    MEMORY_MANAGER.clear_temporary()

    MEMORY_MANAGER.add_temporary(
        "user",
        "Who is Tony Stark?"
    )

    MEMORY_MANAGER.add_temporary(
        "assistant",
        "Tony Stark is Iron Man."
    )

    context = (
        MEMORY_MANAGER
        .build_recent_context()
    )

    if "Tony Stark" not in context:
        raise AssertionError(context)

    return context


# =========================================================
# PERMANENT MEMORY
# =========================================================

def test_permanent_memory_cycle():
    from brain.memory_manager import MEMORY_MANAGER

    MEMORY_MANAGER.forget(
        "phase8_test_memory"
    )

    item = MEMORY_MANAGER.remember(
        "phase8_test_memory",
        "working"
    )

    loaded = MEMORY_MANAGER.get_memory(
        "phase8_test_memory"
    )

    if loaded is None:
        raise AssertionError(
            "Permanent memory missing."
        )

    if loaded.value != "working":
        raise AssertionError(loaded)

    removed = MEMORY_MANAGER.forget(
        "phase8_test_memory"
    )

    if not removed:
        raise AssertionError(
            "Permanent memory was not removed."
        )

    return "Permanent save/read/forget works."


# =========================================================
# RELEVANT MEMORY RETRIEVAL
# =========================================================

def test_relevant_memory():
    from brain.memory_manager import MEMORY_MANAGER

    keys = [
        "preferred browser",
        "favorite editor",
        "favorite game",
    ]

    for key in keys:
        MEMORY_MANAGER.forget(key)

    MEMORY_MANAGER.remember(
        "preferred browser",
        "chrome"
    )

    MEMORY_MANAGER.remember(
        "favorite editor",
        "vscode"
    )

    MEMORY_MANAGER.remember(
        "favorite game",
        "minecraft"
    )

    context = (
        MEMORY_MANAGER
        .build_relevant_permanent_context(
            "which browser do I prefer?"
        )
    )

    if "preferred browser" not in context:
        raise AssertionError(context)

    if "favorite game" in context:
        raise AssertionError(
            "Irrelevant memory leaked into context."
        )

    for key in keys:
        MEMORY_MANAGER.forget(key)

    return context


# =========================================================
# ACTION CONTEXT RESOLVER
# =========================================================

def test_action_context_close():
    from brain.memory_manager import MEMORY_MANAGER
    from brain.action_context_resolver import ActionContextResolver

    MEMORY_MANAGER.clear_temporary()

    MEMORY_MANAGER.add_temporary(
        "user",
        "open notepad",
        metadata={
            "route": "action",
            "intent": "desktop_action",
            "action": "open",
            "target": "notepad",
            "command": "open notepad",
        },
    )

    resolver = ActionContextResolver(
        MEMORY_MANAGER
    )

    result = resolver.resolve_follow_up(
        "close it"
    )

    if result != "close notepad":
        raise AssertionError(result)

    return result


def test_action_context_type():
    from brain.memory_manager import MEMORY_MANAGER
    from brain.action_context_resolver import ActionContextResolver

    MEMORY_MANAGER.clear_temporary()

    MEMORY_MANAGER.add_temporary(
        "user",
        "open notepad",
        metadata={
            "route": "action",
            "intent": "desktop_action",
            "action": "open",
            "target": "notepad",
            "command": "open notepad",
        },
    )

    resolver = ActionContextResolver(
        MEMORY_MANAGER
    )

    result = resolver.resolve_follow_up(
        "type hello in it"
    )

    if result != "type hello":
        raise AssertionError(result)

    return result


def test_action_context_browser():
    from brain.memory_manager import MEMORY_MANAGER
    from brain.action_context_resolver import ActionContextResolver

    MEMORY_MANAGER.clear_temporary()

    MEMORY_MANAGER.add_temporary(
        "user",
        "open chrome",
        metadata={
            "route": "action",
            "intent": "desktop_action",
            "action": "open",
            "target": "chrome",
            "command": "open chrome",
        },
    )

    resolver = ActionContextResolver(
        MEMORY_MANAGER
    )

    result = resolver.resolve_follow_up(
        "now search youtube for python tutorials"
    )

    expected = (
        "search youtube for python tutorials"
    )

    if result != expected:
        raise AssertionError(result)

    return result


# =========================================================
# CONTROLLER MEMORY COMMANDS
# =========================================================

def test_controller_memory_commands():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController
    from actions.desktop_actions import execute_command
    from brain.memory_manager import MEMORY_MANAGER

    MEMORY_MANAGER.forget(
        "preferred browser"
    )

    connect_ollama(AI_ENGINE)

    controller = AIController(
        AI_ENGINE,
        execute_command
    )

    saved = controller.handle(
        "remember that my preferred browser is chrome"
    )

    if (
        not saved.success
        or
        saved.route != "memory"
    ):
        raise AssertionError(saved)

    queried = controller.handle(
        "what do you remember about preferred browser"
    )

    if "chrome" not in queried.text.lower():
        raise AssertionError(queried)

    removed = controller.handle(
        "forget my preferred browser"
    )

    if (
        not removed.success
        or
        removed.route != "memory"
    ):
        raise AssertionError(removed)

    return "Memory command routing works."


# =========================================================
# CONTINUOUS CONVERSATION
# =========================================================

def test_continuous_conversation():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController
    from actions.desktop_actions import execute_command
    from brain.memory_manager import MEMORY_MANAGER

    MEMORY_MANAGER.clear_temporary()

    connect_ollama(AI_ENGINE)

    controller = AIController(
        AI_ENGINE,
        execute_command
    )

    first = controller.handle(
        "Who is Tony Stark?"
    )

    second = controller.handle(
        "What company does he own?"
    )

    if not first.success:
        raise AssertionError(first)

    if not second.success:
        raise AssertionError(second)

    if (
        "stark" not in second.text.lower()
        and
        "industries" not in second.text.lower()
    ):
        raise AssertionError(second)

    return (
        f"Follow-up answer: {second.text}"
    )


# =========================================================
# PERMANENT MEMORY IN NORMAL CONVERSATION
# =========================================================

def test_permanent_memory_in_conversation():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController
    from actions.desktop_actions import execute_command
    from brain.memory_manager import MEMORY_MANAGER

    MEMORY_MANAGER.clear_temporary()
    MEMORY_MANAGER.forget(
        "preferred browser"
    )

    connect_ollama(AI_ENGINE)

    controller = AIController(
        AI_ENGINE,
        execute_command
    )

    controller.handle(
        "remember that my preferred browser is chrome"
    )

    result = controller.handle(
        "which browser do I prefer?"
    )

    MEMORY_MANAGER.forget(
        "preferred browser"
    )

    if not result.success:
        raise AssertionError(result)

    if "chrome" not in result.text.lower():
        raise AssertionError(result)

    return result.text


# =========================================================
# CONTEXTUAL ACTIONS WITH DRY EXECUTOR
# =========================================================

def test_contextual_close_dry():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController
    from brain.memory_manager import MEMORY_MANAGER

    MEMORY_MANAGER.clear_temporary()

    connect_ollama(AI_ENGINE)

    executed = []

    def fake_executor(command):
        executed.append(command)
        return f"DRY: {command}"

    controller = AIController(
        AI_ENGINE,
        fake_executor
    )

    controller.handle(
        "open notepad"
    )

    result = controller.handle(
        "close it"
    )

    if result.action_command != "close notepad":
        raise AssertionError(result)

    return result.action_command


def test_contextual_type_dry():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController
    from brain.memory_manager import MEMORY_MANAGER

    MEMORY_MANAGER.clear_temporary()

    connect_ollama(AI_ENGINE)

    executed = []

    def fake_executor(command):
        executed.append(command)
        return f"DRY: {command}"

    controller = AIController(
        AI_ENGINE,
        fake_executor
    )

    controller.handle(
        "open notepad"
    )

    result = controller.handle(
        "type hello in it"
    )

    if result.action_command != "type hello":
        raise AssertionError(result)

    return result.action_command


def test_contextual_browser_dry():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController
    from brain.memory_manager import MEMORY_MANAGER

    MEMORY_MANAGER.clear_temporary()

    connect_ollama(AI_ENGINE)

    executed = []

    def fake_executor(command):
        executed.append(command)
        return f"DRY: {command}"

    controller = AIController(
        AI_ENGINE,
        fake_executor
    )

    controller.handle(
        "open chrome"
    )

    result = controller.handle(
        "now search youtube for python tutorials"
    )

    expected = (
        "search youtube for python tutorials"
    )

    if result.action_command != expected:
        raise AssertionError(result)

    return result.action_command


# =========================================================
# PHASE 7 REGRESSION SMOKE
# =========================================================

def test_phase7_smoke():
    from brain.ai_engine import AI_ENGINE
    from brain.ollama_backend import connect_ollama
    from brain.ai_controller import AIController

    connect_ollama(AI_ENGINE)

    controller = AIController(
        AI_ENGINE,
        lambda command: f"DRY: {command}",
    )

    conversation = controller.handle(
        "What is Python?"
    )

    action = controller.handle(
        "open notepad"
    )

    multi = controller.handle(
        "open chrome and search youtube for python tutorial"
    )

    if conversation.route != "conversation":
        raise AssertionError(conversation)

    if action.route != "action":
        raise AssertionError(action)

    if multi.route != "multi_action":
        raise AssertionError(multi)

    return (
        "Conversation/action/multi-action routes still work."
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 68)
    print("WizzArc Phase 8 - Memory & Context Regression Test")
    print("=" * 68)
    print()

    run_test(
        "Phase 8 imports",
        test_imports
    )

    run_test(
        "Temporary memory",
        test_temporary_memory
    )

    run_test(
        "Recent conversation context",
        test_recent_context
    )

    run_test(
        "Permanent memory cycle",
        test_permanent_memory_cycle
    )

    run_test(
        "Relevant memory retrieval",
        test_relevant_memory
    )

    run_test(
        "Action context - close it",
        test_action_context_close
    )

    run_test(
        "Action context - type in it",
        test_action_context_type
    )

    run_test(
        "Action context - browser follow-up",
        test_action_context_browser
    )

    run_test(
        "Controller memory commands",
        test_controller_memory_commands
    )

    run_test(
        "Continuous conversation",
        test_continuous_conversation
    )

    run_test(
        "Permanent memory in conversation",
        test_permanent_memory_in_conversation
    )

    run_test(
        "Controller contextual close dry run",
        test_contextual_close_dry
    )

    run_test(
        "Controller contextual type dry run",
        test_contextual_type_dry
    )

    run_test(
        "Controller contextual browser dry run",
        test_contextual_browser_dry
    )

    run_test(
        "Phase 7 controller smoke regression",
        test_phase7_smoke
    )

    print()
    print("=" * 68)
    print(
        f"RESULT: {PASSED} passed, "
        f"{FAILED} failed"
    )
    print("=" * 68)

    # Clean test state.
    try:
        from brain.memory_manager import MEMORY_MANAGER

        for key in [
            "phase8_test_memory",
            "preferred browser",
            "favorite editor",
            "favorite game",
        ]:
            MEMORY_MANAGER.forget(key)

        MEMORY_MANAGER.clear_temporary()

    except Exception:
        pass

    if FAILED == 0:
        print(
            "PHASE 8 REGRESSION TEST: PASS"
        )
        sys.exit(0)

    print(
        "PHASE 8 REGRESSION TEST: FAIL"
    )
    sys.exit(1)