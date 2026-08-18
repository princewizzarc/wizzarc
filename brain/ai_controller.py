import re
from dataclasses import dataclass
from typing import Any, Optional

from brain.ai_router import AIRouter
from brain.tool_executor import ToolExecutor
from brain.multi_step_executor import MultiStepExecutor
from brain.screen_ai import ScreenAI
from brain.memory_manager import MEMORY_MANAGER
from brain.action_context_resolver import ActionContextResolver


# =========================================================
# CONTROLLER RESULT
# =========================================================

@dataclass
class AIControllerResult:
    success: bool
    route: str
    text: str = ""
    action_command: str = ""
    action_result: Any = None
    intent: Any = None
    error: Optional[str] = None
    confirmation_required: bool = False
    dangerous_action: Any = None


# =========================================================
# AI CONTROLLER
# =========================================================

class AIController:

    def __init__(
        self,
        ai_engine,
        command_executor,
        intent_engine=None,
        memory_manager=None,
    ):

        self.ai_engine = ai_engine

        self.router = AIRouter(
            ai_engine=ai_engine,
            intent_engine=intent_engine,
        )

        self.tool_executor = ToolExecutor(
            command_executor=command_executor,
        )

        self.multi_step_executor = MultiStepExecutor(
            ai_engine=ai_engine,
            command_executor=command_executor,
        )

        self.screen_ai = ScreenAI(
            ai_engine=ai_engine,
        )

        self.memory_manager = (
            memory_manager
            or MEMORY_MANAGER
        )


        self.action_context_resolver = (
            ActionContextResolver(
                self.memory_manager
            )
        )



    # =====================================================
    # SCREEN CONTEXT QUESTION HEURISTIC
    # =====================================================

    def is_screen_context_question(
        self,
        user_text,
    ):

        text = (
            str(user_text)
            .lower()
            .strip()
        )

        screen_terms = (
            "screen",
            "visible",
            "see here",
            "see on",
            "what can you see",
            "what do you see",
            "on my display",
        )

        question_terms = (
            "what",
            "which",
            "where",
            "can you see",
            "do you see",
            "is visible",
            "are visible",
        )

        has_screen_reference = any(
            term in text
            for term in screen_terms
        )

        has_question_reference = any(
            term in text
            for term in question_terms
        )

        return (
            has_screen_reference
            and
            has_question_reference
        )

    # =====================================================
    # MULTI-STEP REQUEST HEURISTIC
    # =====================================================

    def is_multi_step_request(
        self,
        user_text,
    ):

        text = (
            str(user_text)
            .lower()
            .strip()
        )

        connectors = (
            " and ",
            " then ",
            " after that ",
            " and then ",
        )

        return any(
            token in text
            for token in connectors
        )


    # =====================================================
    # MEMORY HELPERS
    # =====================================================

    def _build_recent_memory_context(
        self,
        limit=10,
    ):

        return (
            self.memory_manager
            .build_recent_context(
                limit=limit
            )
        )


    def _build_ai_memory_context(
        self,
        user_text,
        recent_limit=10,
        permanent_limit=5,
    ):

        parts = []

        recent = (
            self.memory_manager
            .build_recent_context(
                limit=recent_limit
            )
        )

        permanent = (
            self.memory_manager
            .build_relevant_permanent_context(
                query=user_text,
                limit=permanent_limit,
            )
        )

        if recent:
            parts.append(
                recent
            )

        if permanent:
            parts.append(
                permanent
            )

        return "\n\n".join(
            parts
        )

    def _remember_temporary_exchange(
        self,
        user_text,
        assistant_text,
        route,
        metadata=None,
    ):

        user_metadata = {
            "route": route,
        }

        if isinstance(
            metadata,
            dict
        ):
            user_metadata.update(
                metadata
            )

        try:
            self.memory_manager.add_temporary(
                "user",
                user_text,
                metadata=user_metadata,
            )

            if assistant_text:
                self.memory_manager.add_temporary(
                    "assistant",
                    assistant_text,
                    metadata={
                        "route": route,
                    },
                )

        except Exception:
            # Memory failure must not break the assistant.
            pass


    # =====================================================
    # PERMANENT MEMORY COMMANDS
    # =====================================================

    def _handle_memory_command(
        self,
        user_text,
    ):

        text = str(
            user_text
        ).strip()

        normalized = (
            text.lower()
            .strip()
            .rstrip(".!?")
        )

        # ---------------------------------------------
        # SHOW ALL SAVED MEMORIES
        # ---------------------------------------------

        if normalized in {
            "what do you remember",
            "what do you remember about me",
            "show memories",
            "show memory",
            "show saved memories",
        }:

            memories = (
                self.memory_manager
                .list_memories()
            )

            if not memories:
                return AIControllerResult(
                    success=True,
                    route="memory",
                    text="I don't have any permanent memories saved yet.",
                )

            lines = [
                "Here's what I remember permanently:"
            ]

            for item in memories:
                lines.append(
                    f"- {item.key}: {item.value}"
                )

            return AIControllerResult(
                success=True,
                route="memory",
                text="\n".join(
                    lines
                ),
            )

        # ---------------------------------------------
        # QUERY ONE MEMORY
        # ---------------------------------------------

        query_match = re.match(
            r"^what do you remember about (.+)$",
            normalized,
            flags=re.IGNORECASE,
        )

        if query_match:

            key = (
                query_match
                .group(1)
                .strip()
            )

            memory = (
                self.memory_manager
                .get_memory(
                    key
                )
            )

            if memory is None:
                return AIControllerResult(
                    success=True,
                    route="memory",
                    text=(
                        "I don't have a permanent memory "
                        f"saved for '{key}'."
                    ),
                )

            return AIControllerResult(
                success=True,
                route="memory",
                text=(
                    f"{memory.key}: "
                    f"{memory.value}"
                ),
            )

        # ---------------------------------------------
        # FORGET ONE MEMORY
        # ---------------------------------------------

        forget_match = re.match(
            r"^(?:forget that|remove memory|delete memory|forget) (.+)$",
            normalized,
            flags=re.IGNORECASE,
        )

        if forget_match:

            key = (
                forget_match
                .group(1)
                .strip()
            )

            # Friendly variants:
            # "forget my preferred browser"
            if key.lower().startswith(
                "my "
            ):
                key = key[3:].strip()

            removed = (
                self.memory_manager
                .forget(
                    key
                )
            )

            if removed:
                return AIControllerResult(
                    success=True,
                    route="memory",
                    text=(
                        f"I forgot the permanent memory '{key}'."
                    ),
                )

            return AIControllerResult(
                success=True,
                route="memory",
                text=(
                    "I couldn't find a permanent memory "
                    f"named '{key}'."
                ),
            )

        # ---------------------------------------------
        # REMEMBER KEY = VALUE
        # ---------------------------------------------

        remember_match = re.match(
            r"^(?:remember that|save memory|save that|remember) (.+)$",
            normalized,
            flags=re.IGNORECASE,
        )

        if remember_match:

            statement = (
                remember_match
                .group(1)
                .strip()
            )

            # Supported explicit formats:
            # my preferred browser is chrome
            # preferred browser is chrome
            # preferred browser = chrome
            # preferred browser: chrome
            parsed = re.match(
                r"^(?:my )?(.+?)\s+(?:is|=|:)\s*(.+)$",
                statement,
                flags=re.IGNORECASE,
            )

            if parsed:

                key = (
                    parsed
                    .group(1)
                    .strip()
                )

                value = (
                    parsed
                    .group(2)
                    .strip()
                )

                memory = (
                    self.memory_manager
                    .remember(
                        key,
                        value,
                        metadata={
                            "source": "explicit_user_request",
                        },
                    )
                )

                return AIControllerResult(
                    success=True,
                    route="memory",
                    text=(
                        "Saved permanently: "
                        f"{memory.key} = {memory.value}"
                    ),
                )

            return AIControllerResult(
                success=False,
                route="memory",
                text=(
                    "Tell me what to remember in a clear form, "
                    "for example: "
                    "'remember that my preferred browser is chrome'."
                ),
                error="Could not parse permanent memory request.",
            )

        return None

    # =====================================================
    # PHASE 9.4 - FAST CONVERSATION PATH
    # =====================================================

    def _is_fast_conversation_candidate(
        self,
        user_text,
    ):
        """
        Skip the intent-model call only for messages that are very
        clearly normal conversation / general knowledge.

        Ambiguous desktop commands still go through the normal AI router.
        """

        text = (
            str(user_text)
            .lower()
            .strip()
        )

        if not text:
            return False

        # Anything that looks like desktop/system/browser/file control
        # must keep using the normal intent router.
        action_markers = (
            "open ",
            "close ",
            "launch ",
            "start ",
            "run ",
            "search ",
            "type ",
            "write ",
            "click ",
            "press ",
            "scroll ",
            "move ",
            "copy ",
            "rename ",
            "delete ",
            "remove ",
            "create folder",
            "make folder",
            "volume",
            "brightness",
            "wifi",
            "wi-fi",
            "bluetooth",
            "screenshot",
            "lock computer",
            "shutdown",
            "restart",
            "sleep computer",
            "desktop",
            "downloads",
            "documents",
            "pictures",
            "videos",
            "music folder",
            "drive",
            "window",
            "browser",
            "chrome",
            "edge",
            "notepad",
            "calculator",
            "vscode",
            "discord",
            "file ",
            "files ",
            "folder ",
            "folders ",
            "screen",
        )

        if any(
            marker in text
            for marker in action_markers
        ):
            return False

        # High-confidence normal conversation / knowledge forms.
        conversation_starts = (
            "what is ",
            "what are ",
            "who is ",
            "who are ",
            "who was ",
            "who were ",
            "why is ",
            "why are ",
            "why does ",
            "why do ",
            "how does ",
            "how do ",
            "explain ",
            "explain the ",
            "tell me about ",
            "define ",
            "describe ",
            "compare ",
            "difference between ",
            "meaning of ",
            "hello",
            "hi",
            "hey",
            "thanks",
            "thank you",
            "good morning",
            "good afternoon",
            "good evening",
        )

        return text.startswith(
            conversation_starts
        )

    def _run_conversation(
        self,
        user_text,
        intent=None,
    ):
        """
        Shared conversation response path.
        Keeps Phase 8 memory behavior unchanged.
        """

        memory_context = (
            self._build_ai_memory_context(
                user_text=user_text,
                recent_limit=10,
                permanent_limit=5,
            )
        )

        response = self.ai_engine.generate(
            user_text,
            context=(
                memory_context
                if memory_context
                else None
            ),
        )

        if not response.success:

            return AIControllerResult(
                success=False,
                route="conversation",
                intent=intent,
                error=response.error,
            )

        self._remember_temporary_exchange(
            user_text,
            response.text,
            "conversation",
        )

        return AIControllerResult(
            success=True,
            route="conversation",
            text=response.text,
            intent=intent,
        )

    # =====================================================
    # HANDLE USER MESSAGE
    # =====================================================

    def handle(
        self,
        user_text,
    ):

        user_text = (
            str(user_text)
            .strip()
        )

        # ---------------------------------------------
        # EXPLICIT MEMORY COMMANDS COME FIRST
        # ---------------------------------------------

        memory_result = (
            self._handle_memory_command(
                user_text
            )
        )

        if memory_result is not None:

            try:
                self.memory_manager.add_temporary(
                    "user",
                    user_text,
                    metadata={
                        "route": "memory",
                    },
                )

                if memory_result.text:
                    self.memory_manager.add_temporary(
                        "assistant",
                        memory_result.text,
                        metadata={
                            "route": "memory",
                        },
                    )

            except Exception:
                pass

            return memory_result

        if not user_text:

            return AIControllerResult(
                success=False,
                route="unknown",
                error="User message is empty.",
            )

        # ---------------------------------------------
        # CONTEXTUAL FOLLOW-UP ACTION
        # ---------------------------------------------

        contextual_command = (
            self.action_context_resolver
            .resolve_follow_up(
                user_text
            )
        )

        if contextual_command:

            execution = (
                self.tool_executor
                .execute_command(
                    contextual_command
                )
            )

            if execution.confirmation_required:
                return AIControllerResult(
                    success=False,
                    route="confirmation",
                    text="Confirmation required.",
                    action_command=(
                        execution.command
                    ),
                    action_result=execution,
                    error=execution.error,
                    confirmation_required=True,
                    dangerous_action=(
                        execution.dangerous_action
                    ),
                )

            if not execution.success:
                return AIControllerResult(
                    success=False,
                    route="action",
                    action_command=(
                        execution.command
                    ),
                    error=execution.error,
                )

            raw_execution_result = (
                execution.result
            )

            result_text = (
                str(raw_execution_result)
                if raw_execution_result is not None
                else ""
            )

            contextual_action = ""
            contextual_target = ""

            if contextual_command.startswith(
                "close "
            ):
                contextual_action = "close"
                contextual_target = (
                    contextual_command[
                        len("close "):
                    ].strip()
                )

            elif contextual_command.startswith(
                "switch to "
            ):
                contextual_action = "switch_to"
                contextual_target = (
                    contextual_command[
                        len("switch to "):
                    ].strip()
                )

            elif contextual_command.startswith(
                "type "
            ):
                contextual_action = "type_text"
                contextual_target = (
                    self.action_context_resolver
                    .get_last_action_context()
                    .last_target
                )

            elif contextual_command.startswith(
                "search youtube for "
            ):
                contextual_action = "search_youtube"
                contextual_target = (
                    contextual_command[
                        len("search youtube for "):
                    ].strip()
                )

            elif contextual_command.startswith(
                "search google for "
            ):
                contextual_action = "search_google"
                contextual_target = (
                    contextual_command[
                        len("search google for "):
                    ].strip()
                )

            self._remember_temporary_exchange(
                user_text,
                result_text,
                "action",
                metadata={
                    "intent": (
                        "browser_action"
                        if contextual_action in {
                            "search_youtube",
                            "search_google",
                        }
                        else "desktop_action"
                    ),
                    "action": contextual_action,
                    "target": contextual_target,
                    "command": contextual_command,
                    "contextual": True,
                },
            )

            return AIControllerResult(
                success=True,
                route="action",
                text=result_text,
                action_command=contextual_command,
                action_result=raw_execution_result,
            )

        # ---------------------------------------------
        # SCREEN-AWARE QUESTION
        # ---------------------------------------------

        if self.is_screen_context_question(
            user_text
        ):

            screen_result = self.screen_ai.ask(
                user_text
            )

            if screen_result.success:

                self._remember_temporary_exchange(
                    user_text,
                    screen_result.text,
                    "screen_context",
                )

                return AIControllerResult(
                    success=True,
                    route="screen_context",
                    text=screen_result.text,
                )

            # If screen context fails, continue to the
            # normal router instead of crashing.

        # ---------------------------------------------
        # MULTI-STEP ACTION REQUEST
        # ---------------------------------------------

        if self.is_multi_step_request(
            user_text
        ):

            multi_result = (
                self.multi_step_executor.execute(
                    user_text
                )
            )

            if multi_result.confirmation_required:
                return AIControllerResult(
                    success=False,
                    route="confirmation",
                    text="Confirmation required.",
                    action_command=(
                        multi_result.pending_command
                    ),
                    action_result=multi_result,
                    error=multi_result.error,
                    confirmation_required=True,
                    dangerous_action=(
                        multi_result.dangerous_action
                    ),
                )

            if multi_result.success:

                summary_lines = []

                for step in multi_result.steps:

                    summary_lines.append(
                        (
                            f"Step {step.step_number}: "
                            f"{step.result}"
                        )
                    )

                summary_text = "\n".join(
                    summary_lines
                )

                last_step = (
                    multi_result.plan.steps[-1]
                    if (
                        multi_result.plan
                        and
                        getattr(
                            multi_result.plan,
                            "steps",
                            None
                        )
                    )
                    else None
                )

                multi_metadata = {}

                if last_step is not None:
                    multi_metadata = {
                        "intent": last_step.intent,
                        "action": last_step.action,
                        "target": last_step.target,
                        "command": (
                            multi_result.steps[-1].command
                            if multi_result.steps
                            else ""
                        ),
                    }

                self._remember_temporary_exchange(
                    user_text,
                    summary_text,
                    "multi_action",
                    metadata=multi_metadata,
                )

                return AIControllerResult(
                    success=True,
                    route="multi_action",
                    text=summary_text,
                    action_result=multi_result,
                )

            # If planning/execution fails, fall back
            # to normal single-intent routing below.

        # ---------------------------------------------
        # FAST NORMAL CONVERSATION
        # ---------------------------------------------
        # Clear general-knowledge/chat messages do not need a separate
        # intent-classification model call first.
        if self._is_fast_conversation_candidate(
            user_text
        ):
            return self._run_conversation(
                user_text
            )

        route_result = self.router.route(
            user_text
        )

        # ---------------------------------------------
        # CONVERSATION
        # ---------------------------------------------

        if (
            route_result.success
            and
            route_result.route
            == "conversation"
        ):

            return self._run_conversation(
                user_text,
                intent=route_result.intent,
            )

        # ---------------------------------------------
        # ACTION
        # ---------------------------------------------

        if (
            route_result.success
            and
            route_result.route
            == "action"
        ):

            execution = (
                self.tool_executor.execute(
                    route_result.intent
                )
            )

            if execution.confirmation_required:

                return AIControllerResult(
                    success=False,
                    route="confirmation",
                    text="Confirmation required.",
                    intent=route_result.intent,
                    action_command=execution.command,
                    action_result=execution,
                    error=execution.error,
                    confirmation_required=True,
                    dangerous_action=(
                        execution.dangerous_action
                    ),
                )

            if not execution.success:

                return AIControllerResult(
                    success=False,
                    route="action",
                    intent=route_result.intent,
                    action_command=execution.command,
                    error=execution.error,
                )

            result_text = (
                str(
                    execution.result
                )
                if execution.result is not None
                else ""
            )

            self._remember_temporary_exchange(
                user_text,
                result_text,
                "action",
                metadata={
                    "intent": route_result.intent.intent,
                    "action": route_result.intent.action,
                    "target": route_result.intent.target,
                    "command": execution.command,
                },
            )

            return AIControllerResult(
                success=True,
                route="action",
                text=result_text,
                intent=route_result.intent,
                action_command=execution.command,
                action_result=execution.result,
            )

        # ---------------------------------------------
        # UNKNOWN / FAILED
        # ---------------------------------------------

        return AIControllerResult(
            success=False,
            route=route_result.route,
            intent=route_result.intent,
            error=(
                route_result.error
                or
                "AI routing failed."
            ),
        )


# =========================================================
# FACTORY
# =========================================================

def create_ai_controller(
    ai_engine,
    command_executor,
    intent_engine=None,
    memory_manager=None,
):

    return AIController(
        ai_engine=ai_engine,
        command_executor=command_executor,
        intent_engine=intent_engine,
        memory_manager=memory_manager,
    )