from dataclasses import dataclass
from typing import Any, Optional

from brain.intent_engine import IntentEngine


# =========================================================
# ROUTE RESULT
# =========================================================

@dataclass
class AIRouteResult:
    route: str
    text: str = ""
    intent: Any = None
    success: bool = True
    error: Optional[str] = None


# =========================================================
# AI ROUTER
# =========================================================

class AIRouter:

    ACTION_INTENTS = {
        "desktop_action",
        "screen_action",
        "browser_action",
        "file_action",
        "automation_action",
    }

    def __init__(
        self,
        ai_engine,
        intent_engine=None,
    ):
        self.ai_engine = ai_engine
        self.intent_engine = (
            intent_engine
            or IntentEngine(ai_engine)
        )

    def route(self, user_text):

        user_text = str(
            user_text
        ).strip()

        if not user_text:
            return AIRouteResult(
                route="unknown",
                success=False,
                error="User message is empty.",
            )

        intent = self.intent_engine.understand(
            user_text
        )

        # ---------------------------------------------
        # CONVERSATION
        # ---------------------------------------------

        if intent.intent == "conversation":

            # If the intent parser already supplied a
            # useful conversational reply, use it.
            if intent.reply:
                return AIRouteResult(
                    route="conversation",
                    text=intent.reply,
                    intent=intent,
                )

            response = self.ai_engine.generate(
                user_text
            )

            if not response.success:
                return AIRouteResult(
                    route="conversation",
                    intent=intent,
                    success=False,
                    error=response.error,
                )

            return AIRouteResult(
                route="conversation",
                text=response.text,
                intent=intent,
            )

        # ---------------------------------------------
        # ACTION
        # ---------------------------------------------

        if intent.intent in self.ACTION_INTENTS:

            return AIRouteResult(
                route="action",
                intent=intent,
                text="",
            )

        # ---------------------------------------------
        # UNKNOWN
        # ---------------------------------------------

        return AIRouteResult(
            route="unknown",
            intent=intent,
            success=False,
            error=(
                "I couldn't confidently determine "
                "whether this is a conversation "
                "or an action."
            ),
        )


def create_ai_router(
    ai_engine,
    intent_engine=None,
):
    return AIRouter(
        ai_engine=ai_engine,
        intent_engine=intent_engine,
    )