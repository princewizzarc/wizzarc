import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class IntentResult:
    intent: str
    action: str = ""
    target: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    reply: str = ""
    confidence: float = 0.0
    raw: Any = None


class IntentEngine:

    ALLOWED_INTENTS = {
        "conversation",
        "desktop_action",
        "screen_action",
        "browser_action",
        "file_action",
        "automation_action",
        "unknown",
    }

    def __init__(self, ai_engine):
        self.ai_engine = ai_engine

    def _build_prompt(self, user_text):
        return f"""
You are WizzArc's intent parser.
Return exactly ONE valid JSON object and nothing else.
Never explain your reasoning.
Never output <think> tags.
Never use markdown.

Allowed intents:
conversation, desktop_action, screen_action, browser_action,
file_action, automation_action, unknown

Schema:
{{
  "intent": "allowed intent",
  "action": "short normalized action or empty string",
  "target": "main target or empty string",
  "parameters": {{}},
  "reply": "only for conversation, otherwise empty string",
  "confidence": 0.0
}}

Examples:
open notepad
{{"intent":"desktop_action","action":"open","target":"notepad","parameters":{{}},"reply":"","confidence":0.98}}

click terminal on screen
{{"intent":"screen_action","action":"click_text","target":"terminal","parameters":{{}},"reply":"","confidence":0.97}}

what can you see on my screen
{{"intent":"screen_action","action":"screen_summary","target":"","parameters":{{}},"reply":"","confidence":0.98}}

User message: {user_text}

JSON:
""".strip()

    def _extract_json(self, text):
        text = str(text).strip()

        # -------------------------------------------------
        # QWEN THINKING OUTPUT CLEANUP
        # -------------------------------------------------
        # Keep only the content after the LAST </think>.
        # Qwen can sometimes expose reasoning without an
        # opening <think> tag.
        lower_text = text.lower()
        closing_index = lower_text.rfind(
            "</think>"
        )

        if closing_index != -1:
            text = text[
                closing_index
                + len("</think>"):
            ].strip()

        # Support normal paired tags too.
        text = re.sub(
            r"<think>.*?</think>",
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        ).strip()

        # Remove accidental markdown fences.
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        ).strip()

        # -------------------------------------------------
        # FAST PATH: WHOLE RESPONSE IS JSON
        # -------------------------------------------------
        try:
            value = json.loads(
                text
            )

            if (
                isinstance(
                    value,
                    dict
                )
                and
                "intent" in value
            ):
                return value

        except json.JSONDecodeError:
            pass

        # -------------------------------------------------
        # RECOVERY: FIND ALL JSON OBJECTS
        # -------------------------------------------------
        # Important: nested objects such as "parameters": {}
        # are also valid JSON. So NEVER simply return the
        # last dictionary. Only accept an object containing
        # the required top-level "intent" field.
        decoder = json.JSONDecoder()

        valid_intent_objects = []

        for index, char in enumerate(
            text
        ):

            if char != "{":
                continue

            try:
                value, _ = (
                    decoder.raw_decode(
                        text[
                            index:
                        ]
                    )
                )

            except json.JSONDecodeError:
                continue

            if (
                isinstance(
                    value,
                    dict
                )
                and
                "intent" in value
            ):
                valid_intent_objects.append(
                    value
                )

        if not valid_intent_objects:
            raise ValueError(
                "AI did not return a valid "
                "top-level intent JSON object."
            )

        return valid_intent_objects[
            -1
        ]

    def _generate_intent_text(
        self,
        prompt
    ):

        backend = getattr(
            self.ai_engine,
            "backend",
            None
        )

        if backend is None:

            raise RuntimeError(
                "No AI backend is connected."
            )

        result = backend(
            prompt
        )

        if isinstance(
            result,
            dict
        ):

            text = (
                result.get("text")
                or result.get("response")
                or result.get("content")
                or ""
            )

        else:

            text = str(result)

        return str(text).strip()

    def _is_usable_intent(self, data):
        if not isinstance(data, dict) or not data:
            return False

        intent = str(
            data.get("intent", "")
        ).strip().lower()

        if intent not in self.ALLOWED_INTENTS:
            return False

        # "unknown" is allowed only when the model explicitly
        # produced it; an empty object must never count as success.
        return True

    def understand(self, user_text, max_attempts=2):
        user_text = str(user_text).strip()

        if not user_text:
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                raw={"error": "User message is empty."},
            )

        last_error = None
        last_response = None

        for attempt in range(1, max_attempts + 1):

            prompt = self._build_prompt(user_text)

            if attempt > 1:
                prompt += (
                    "\n\nIMPORTANT RETRY: Your previous output was invalid "
                    "or empty. Return the complete JSON object now. "
                    "Do not return {}. Do not explain."
                )

            try:
                response_text = self._generate_intent_text(
                    prompt
                )

            except Exception as error:
                last_error = str(error)
                continue

            last_response = response_text

            try:
                data = self._extract_json(
                    response_text
                )
            except Exception as error:
                last_error = str(error)
                continue

            if not self._is_usable_intent(data):
                last_error = (
                    "AI returned an empty or invalid intent object."
                )
                continue

            intent = str(
                data.get("intent", "unknown")
            ).strip().lower()

            parameters = data.get("parameters", {})
            if not isinstance(parameters, dict):
                parameters = {}

            try:
                confidence = float(
                    data.get("confidence", 0.0)
                )
            except (TypeError, ValueError):
                confidence = 0.0

            confidence = max(
                0.0,
                min(confidence, 1.0)
            )

            return IntentResult(
                intent=intent,
                action=str(
                    data.get("action", "")
                ).strip(),
                target=str(
                    data.get("target", "")
                ).strip(),
                parameters=parameters,
                reply=str(
                    data.get("reply", "")
                ).strip(),
                confidence=confidence,
                raw={
                    "attempt": attempt,
                    "data": data,
                },
            )

        return IntentResult(
            intent="unknown",
            confidence=0.0,
            raw={
                "error": last_error or "Intent parsing failed.",
                "response": last_response,
                "attempts": max_attempts,
            },
        )


def create_intent_engine(ai_engine):
    return IntentEngine(ai_engine)