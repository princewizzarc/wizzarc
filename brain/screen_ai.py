from dataclasses import dataclass
from typing import Optional

from brain.screen_context_provider import ScreenContextProvider


@dataclass
class ScreenAIResult:
    success: bool
    text: str = ""
    context_used: bool = False
    error: Optional[str] = None


class ScreenAI:

    def __init__(self, ai_engine, context_provider=None):
        self.ai_engine = ai_engine
        self.context_provider = (
            context_provider
            or ScreenContextProvider()
        )

    def ask(self, question, refresh_screen=False):
        question = str(question).strip()

        if not question:
            return ScreenAIResult(
                success=False,
                error="Question is empty.",
            )

        context = self.context_provider.get_context(
            refresh=refresh_screen
        )

        if not context.available:
            return ScreenAIResult(
                success=False,
                error=(
                    context.error
                    or
                    "Screen context is unavailable."
                ),
            )

        prompt = (
            "You are WizzArc's screen-aware AI.\n"
            "Answer only from the provided current screen context.\n"
            "Do not invent elements that are not visible.\n"
            "If the context is unclear, say that clearly.\n\n"
            f"{context.to_prompt_context()}\n\n"
            f"User question: {question}\n"
            "Answer:"
        )

        response = self.ai_engine.generate(prompt)

        if not response.success:
            return ScreenAIResult(
                success=False,
                error=response.error,
            )

        return ScreenAIResult(
            success=True,
            text=response.text,
            context_used=True,
        )


def create_screen_ai(ai_engine, context_provider=None):
    return ScreenAI(
        ai_engine=ai_engine,
        context_provider=context_provider,
    )