from dataclasses import dataclass
from typing import Optional


@dataclass
class ActionContext:
    last_route: str = ""
    last_intent: str = ""
    last_action: str = ""
    last_target: str = ""
    last_command: str = ""
    last_result: str = ""


class ActionContextResolver:

    def __init__(
        self,
        memory_manager,
    ):
        self.memory_manager = memory_manager

    def get_last_action_context(
        self,
    ) -> ActionContext:

        items = (
            self.memory_manager
            .get_temporary(
                limit=12
            )
        )

        last_user = None
        last_assistant = None

        for item in reversed(items):

            route = str(
                item.metadata.get(
                    "route",
                    ""
                )
            ).strip()

            if (
                item.role == "assistant"
                and
                last_assistant is None
            ):
                last_assistant = item

            if (
                item.role == "user"
                and
                route in {
                    "action",
                    "multi_action",
                }
            ):
                last_user = item
                break

        if last_user is None:
            return ActionContext()

        metadata = (
            last_user.metadata
            if isinstance(
                last_user.metadata,
                dict
            )
            else {}
        )

        return ActionContext(
            last_route=str(
                metadata.get(
                    "route",
                    ""
                )
            ),
            last_intent=str(
                metadata.get(
                    "intent",
                    ""
                )
            ),
            last_action=str(
                metadata.get(
                    "action",
                    ""
                )
            ),
            last_target=str(
                metadata.get(
                    "target",
                    ""
                )
            ),
            last_command=str(
                metadata.get(
                    "command",
                    ""
                )
            ),
            last_result=(
                last_assistant.content
                if last_assistant is not None
                else ""
            ),
        )

    def build_context_prompt(
        self,
    ) -> str:

        ctx = (
            self.get_last_action_context()
        )

        if not any(
            [
                ctx.last_intent,
                ctx.last_action,
                ctx.last_target,
                ctx.last_command,
            ]
        ):
            return ""

        lines = [
            "RECENT ACTION CONTEXT:"
        ]

        if ctx.last_intent:
            lines.append(
                f"- intent: {ctx.last_intent}"
            )

        if ctx.last_action:
            lines.append(
                f"- action: {ctx.last_action}"
            )

        if ctx.last_target:
            lines.append(
                f"- target: {ctx.last_target}"
            )

        if ctx.last_command:
            lines.append(
                f"- command: {ctx.last_command}"
            )

        if ctx.last_result:
            lines.append(
                f"- result: {ctx.last_result}"
            )

        return "\n".join(
            lines
        )

    def resolve_follow_up(
        self,
        user_text: str,
    ) -> Optional[str]:

        original = str(
            user_text
        ).strip()

        text = (
            original
            .lower()
            .strip()
        )

        if not text:
            return None

        ctx = (
            self.get_last_action_context()
        )

        if not ctx.last_target:
            return None

        # ---------------------------------------------
        # CLOSE / SWITCH PREVIOUS TARGET
        # ---------------------------------------------

        if text in {
            "close it",
            "close this",
            "close that",
        }:
            return (
                f"close {ctx.last_target}"
            )

        if text in {
            "switch to it",
            "switch to this",
            "switch to that",
        }:
            return (
                f"switch to {ctx.last_target}"
            )

        # ---------------------------------------------
        # TYPE INTO CURRENT/PREVIOUS APP
        # ---------------------------------------------
        # Example:
        # open notepad
        # type hello in it
        #
        # The previously opened app is already focused,
        # so the actual WizzArc command can simply be
        # "type hello".

        type_prefixes = (
            "type ",
            "write ",
        )

        if text.startswith(
            type_prefixes
        ):

            content = original

            if text.startswith(
                "type "
            ):
                content = original[
                    len("type "):
                ].strip()

            elif text.startswith(
                "write "
            ):
                content = original[
                    len("write "):
                ].strip()

            lower_content = (
                content
                .lower()
                .strip()
            )

            suffixes = (
                " in it",
                " into it",
                " in this",
                " into this",
                " there",
            )

            for suffix in suffixes:

                if lower_content.endswith(
                    suffix
                ):
                    content = content[
                        :-len(suffix)
                    ].strip()

                    break

            if content:
                return (
                    f"type {content}"
                )

        # ---------------------------------------------
        # FOLLOW-UP YOUTUBE SEARCH
        # ---------------------------------------------
        # Example:
        # open chrome
        # now search youtube for python tutorials

        youtube_prefixes = (
            "now search youtube for ",
            "then search youtube for ",
            "search youtube for ",
            "now search on youtube for ",
        )

        for prefix in youtube_prefixes:

            if text.startswith(
                prefix
            ):

                query = original[
                    len(prefix):
                ].strip()

                if query:
                    return (
                        f"search youtube for {query}"
                    )

        # ---------------------------------------------
        # FOLLOW-UP GOOGLE SEARCH
        # ---------------------------------------------

        google_prefixes = (
            "now search google for ",
            "then search google for ",
            "search google for ",
            "now search on google for ",
        )

        for prefix in google_prefixes:

            if text.startswith(
                prefix
            ):

                query = original[
                    len(prefix):
                ].strip()

                if query:
                    return (
                        f"search google for {query}"
                    )

        return None
