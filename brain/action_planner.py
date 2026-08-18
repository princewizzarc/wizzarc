import json
import re
from dataclasses import dataclass, field
from typing import Any, List, Optional

from brain.intent_engine import IntentResult


# =========================================================
# PLAN STEP
# =========================================================

@dataclass
class PlanStep:
    number: int
    intent: str
    action: str = ""
    target: str = ""
    parameters: dict = field(default_factory=dict)
    confidence: float = 0.0


# =========================================================
# PLAN RESULT
# =========================================================

@dataclass
class PlanResult:
    success: bool
    steps: List[PlanStep] = field(default_factory=list)
    error: Optional[str] = None
    raw: Any = None


# =========================================================
# ACTION PLANNER
# =========================================================

class ActionPlanner:

    ALLOWED_INTENTS = {
        "desktop_action",
        "screen_action",
        "browser_action",
        "file_action",
        "automation_action",
    }

    MAX_STEPS = 8

    def __init__(
        self,
        ai_engine,
    ):
        self.ai_engine = ai_engine

    # =====================================================
    # PROMPT
    # =====================================================

    def _build_prompt(
        self,
        user_text
    ):
        return f"""
You are WizzArc's multi-step action planner.

Convert the user's request into an ordered JSON plan.
Return exactly ONE JSON object and nothing else.
Never explain your reasoning.
Never use markdown.
Never output think tags.
Do not invent steps the user did not request.

Allowed action intents:
- desktop_action
- screen_action
- browser_action
- file_action
- automation_action

Return this schema:
{{
  "steps": [
    {{
      "intent": "allowed action intent",
      "action": "short normalized action",
      "target": "main target or empty string",
      "parameters": {{}},
      "confidence": 0.0
    }}
  ]
}}

Examples:

User: open chrome and search youtube for python tutorial
{{
  "steps": [
    {{
      "intent": "desktop_action",
      "action": "open",
      "target": "chrome",
      "parameters": {{}},
      "confidence": 0.98
    }},
    {{
      "intent": "browser_action",
      "action": "search_youtube",
      "target": "python tutorial",
      "parameters": {{}},
      "confidence": 0.97
    }}
  ]
}}

User: click terminal and then type python main.py
{{
  "steps": [
    {{
      "intent": "screen_action",
      "action": "click_text",
      "target": "terminal",
      "parameters": {{}},
      "confidence": 0.96
    }},
    {{
      "intent": "desktop_action",
      "action": "type_text",
      "target": "python main.py",
      "parameters": {{}},
      "confidence": 0.95
    }}
  ]
}}

User message:
{user_text}

JSON:
""".strip()

    # =====================================================
    # STATELESS MODEL CALL
    # =====================================================

    def _generate_text(
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

    # =====================================================
    # JSON EXTRACTION
    # =====================================================

    def _extract_json(
        self,
        text
    ):

        text = str(text).strip()

        lower = text.lower()
        closing_index = lower.rfind(
            "</think>"
        )

        if closing_index != -1:
            text = text[
                closing_index
                + len("</think>"):
            ].strip()

        text = re.sub(
            r"<think>.*?</think>",
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        ).strip()

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

        try:
            value = json.loads(
                text
            )

            if (
                isinstance(value, dict)
                and
                isinstance(
                    value.get("steps"),
                    list
                )
            ):
                return value

        except json.JSONDecodeError:
            pass

        decoder = json.JSONDecoder()
        valid = []

        for index, char in enumerate(
            text
        ):
            if char != "{":
                continue

            try:
                value, _ = decoder.raw_decode(
                    text[index:]
                )
            except json.JSONDecodeError:
                continue

            if (
                isinstance(value, dict)
                and
                isinstance(
                    value.get("steps"),
                    list
                )
            ):
                valid.append(
                    value
                )

        if not valid:
            raise ValueError(
                "AI did not return a valid plan JSON object."
            )

        return valid[-1]

    # =====================================================
    # VALIDATE STEP
    # =====================================================

    def _validate_step(
        self,
        item,
        number
    ):

        if not isinstance(
            item,
            dict
        ):
            return None

        intent = str(
            item.get(
                "intent",
                ""
            )
        ).strip().lower()

        if intent not in self.ALLOWED_INTENTS:
            return None

        action = str(
            item.get(
                "action",
                ""
            )
        ).strip().lower()

        target = str(
            item.get(
                "target",
                ""
            )
        ).strip()

        parameters = item.get(
            "parameters",
            {}
        )

        if not isinstance(
            parameters,
            dict
        ):
            parameters = {}

        try:
            confidence = float(
                item.get(
                    "confidence",
                    0.0
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            confidence = 0.0

        confidence = max(
            0.0,
            min(
                confidence,
                1.0
            )
        )

        if not action:
            return None

        return PlanStep(
            number=number,
            intent=intent,
            action=action,
            target=target,
            parameters=parameters,
            confidence=confidence,
        )

    # =====================================================
    # PLAN
    # =====================================================

    def plan(
        self,
        user_text,
        max_attempts=2
    ):

        user_text = str(
            user_text
        ).strip()

        if not user_text:
            return PlanResult(
                success=False,
                error="User request is empty.",
            )

        last_error = None
        last_response = None

        for attempt in range(
            1,
            max_attempts + 1
        ):

            prompt = self._build_prompt(
                user_text
            )

            if attempt > 1:
                prompt += (
                    "\n\nIMPORTANT RETRY: Return a complete "
                    "non-empty steps array. JSON only."
                )

            try:
                response_text = (
                    self._generate_text(
                        prompt
                    )
                )

                last_response = (
                    response_text
                )

                data = self._extract_json(
                    response_text
                )

            except Exception as error:
                last_error = str(error)
                continue

            raw_steps = data.get(
                "steps",
                []
            )

            if not raw_steps:
                last_error = (
                    "AI returned an empty plan."
                )
                continue

            steps = []

            for index, item in enumerate(
                raw_steps[:self.MAX_STEPS],
                start=1
            ):

                step = self._validate_step(
                    item,
                    index
                )

                if step is None:
                    continue

                steps.append(
                    step
                )

            if not steps:
                last_error = (
                    "AI plan contained no valid action steps."
                )
                continue

            return PlanResult(
                success=True,
                steps=steps,
                raw={
                    "attempt":
                        attempt,

                    "data":
                        data,
                },
            )

        return PlanResult(
            success=False,
            error=(
                last_error
                or
                "Planning failed."
            ),
            raw={
                "response":
                    last_response,

                "attempts":
                    max_attempts,
            },
        )


# =========================================================
# PLAN STEP -> INTENT RESULT
# =========================================================

def plan_step_to_intent(
    step
):

    return IntentResult(
        intent=step.intent,
        action=step.action,
        target=step.target,
        parameters=step.parameters,
        confidence=step.confidence,
        raw={
            "plan_step":
                step.number,
        },
    )


def create_action_planner(
    ai_engine
):
    return ActionPlanner(
        ai_engine
    )