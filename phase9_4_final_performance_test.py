from brain.ai_engine import AI_ENGINE
from brain.ollama_backend import connect_ollama
from brain.ai_controller import AIController


def main():

    backend = connect_ollama(
        AI_ENGINE
    )

    if getattr(
        backend,
        "keep_alive",
        None,
    ) != "30m":
        raise AssertionError(
            "Ollama keep_alive should be 30m."
        )

    print(
        "[PASS] Ollama model keep-alive = 30m"
    )

    controller = AIController(
        AI_ENGINE,
        lambda command: f"DRY: {command}",
    )

    if not controller._is_fast_conversation_candidate(
        "What is Python?"
    ):
        raise AssertionError(
            "Normal conversation fast path is not active."
        )

    if controller._is_fast_conversation_candidate(
        "open notepad"
    ):
        raise AssertionError(
            "Desktop command incorrectly entered fast conversation path."
        )

    print(
        "[PASS] Fast conversation optimization active"
    )

    print(
        "[PASS] Desktop commands remain AI-routed"
    )

    print()
    print(
        "PHASE 9.4 PERFORMANCE CONFIG: PASS"
    )


if __name__ == "__main__":
    main()