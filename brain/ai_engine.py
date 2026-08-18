import re
from dataclasses import dataclass
from typing import Callable, Optional, Any


@dataclass
class AIResponse:
    text: str
    success: bool = True
    error: Optional[str] = None
    raw: Any = None


class AIEngine:

    def __init__(
        self,
        model_name="local-model",
        backend: Optional[Callable] = None,
        system_prompt=None,
    ):
        self.model_name = str(model_name).strip() or "local-model"
        self.backend = backend
        self.system_prompt = system_prompt or (
            "You are WizzArc, a local desktop AI assistant. "
            "Understand the user's request clearly and respond concisely. "
            "Do not invent actions that were not requested."
        )
        self.history = []

    def set_backend(self, backend):
        if backend is not None and not callable(backend):
            raise TypeError("AI backend must be callable.")
        self.backend = backend

    def clear_history(self):
        self.history.clear()
        return "AI conversation history cleared."

    def build_prompt(self, user_text, context=None):
        user_text = str(user_text).strip()

        context_text = ""
        if context:
            context_text = "\n\nContext:\n" + str(context).strip()

        history_text = ""
        if self.history:
            recent_history = self.history[-6:]
            lines = []
            for item in recent_history:
                role = item.get("role", "unknown")
                content = item.get("content", "")
                lines.append(f"{role}: {content}")
            history_text = "\n\nRecent conversation:\n" + "\n".join(lines)

        return (
            f"{self.system_prompt}"
            f"{history_text}"
            f"{context_text}"
            f"\n\nUser: {user_text}"
            f"\nAssistant:"
        )

    def generate(self, user_text, context=None):
        user_text = str(user_text).strip()

        if not user_text:
            return AIResponse(
                text="",
                success=False,
                error="User message is empty."
            )

        if self.backend is None:
            return AIResponse(
                text="",
                success=False,
                error="No local AI backend is connected yet."
            )

        prompt = self.build_prompt(user_text, context=context)

        try:
            result = self.backend(prompt)

            if isinstance(result, AIResponse):
                response = result
            elif isinstance(result, dict):
                text = (
                    result.get("text")
                    or result.get("response")
                    or result.get("content")
                    or ""
                )
                response = AIResponse(
                    text=str(text).strip(),
                    success=True,
                    raw=result
                )
            else:
                response = AIResponse(
                    text=str(result).strip(),
                    success=True,
                    raw=result
                )

            if not response.text:
                return AIResponse(
                    text="",
                    success=False,
                    error="The AI backend returned an empty response.",
                    raw=response.raw
                )

            self.history.append({
                "role": "user",
                "content": user_text,
            })

            self.history.append({
                "role": "assistant",
                "content": response.text,
            })

            return response

        except Exception as error:
            return AIResponse(
                text="",
                success=False,
                error=f"AI backend error: {error}"
            )

    def status(self):
        if self.backend is None:
            return {
                "ready": False,
                "model": self.model_name,
                "message": (
                    "AI engine is ready, but no local model backend is connected."
                ),
            }

        return {
            "ready": True,
            "model": self.model_name,
            "message": "AI engine and backend are connected.",
        }


AI_ENGINE = AIEngine()