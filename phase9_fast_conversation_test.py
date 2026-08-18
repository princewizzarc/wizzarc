from brain.ai_controller import AIController


class DummyResponse:
    success = True
    text = "dummy"
    error = None


class DummyAI:
    def generate(
        self,
        user_text,
        context=None,
    ):
        return DummyResponse()


def main():

    controller = AIController(
        DummyAI(),
        lambda command: f"DRY: {command}",
    )

    fast_yes = [
        "What is Python?",
        "Explain recursion",
        "Tell me about artificial intelligence",
        "Who is Alan Turing?",
        "Hello",
    ]

    fast_no = [
        "open notepad",
        "what files are in downloads",
        "tell me about my screen",
        "how do I open chrome",
        "search youtube for python",
    ]

    for text in fast_yes:
        if not controller._is_fast_conversation_candidate(
            text
        ):
            raise AssertionError(
                f"Expected fast conversation: {text}"
            )

    for text in fast_no:
        if controller._is_fast_conversation_candidate(
            text
        ):
            raise AssertionError(
                f"Should use normal router: {text}"
            )

    print(
        "[PASS] Fast conversation candidates"
    )
    print(
        "[PASS] Desktop/action requests stay on normal router"
    )


if __name__ == "__main__":
    main()