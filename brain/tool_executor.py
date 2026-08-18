from dataclasses import dataclass
from typing import Any, Optional

from core.action_safety import classify_dangerous_action


# =========================================================
# TOOL EXECUTION RESULT
# =========================================================

@dataclass
class ToolExecutionResult:
    success: bool
    command: str = ""
    result: Any = None
    error: Optional[str] = None
    intent: Any = None
    confirmation_required: bool = False
    dangerous_action: Any = None


# =========================================================
# TOOL EXECUTOR
# =========================================================

class ToolExecutor:

    def __init__(
        self,
        command_executor,
    ):
        if not callable(command_executor):
            raise TypeError(
                "command_executor must be callable."
            )

        self.command_executor = (
            command_executor
        )

    # =====================================================
    # INTENT -> WIZZARC COMMAND
    # =====================================================

    def build_command(
        self,
        intent
    ):

        if intent is None:
            return None

        intent_type = str(
            getattr(
                intent,
                "intent",
                ""
            )
        ).strip().lower()

        action = str(
            getattr(
                intent,
                "action",
                ""
            )
        ).strip().lower()

        target = str(
            getattr(
                intent,
                "target",
                ""
            )
        ).strip()

        parameters = getattr(
            intent,
            "parameters",
            {}
        )

        if not isinstance(
            parameters,
            dict
        ):
            parameters = {}

        # ---------------------------------------------
        # DESKTOP ACTIONS
        # ---------------------------------------------

        if intent_type == "desktop_action":

            if (
                action == "open"
                and
                target
            ):
                return (
                    f"open {target}"
                )

            if (
                action == "close"
                and
                target
            ):
                return (
                    f"close {target}"
                )

            if action in {
                "volume_up",
                "volume_down",
                "mute",
            }:
                mapping = {
                    "volume_up":
                        "volume up",

                    "volume_down":
                        "volume down",

                    "mute":
                        "mute",
                }

                return mapping[
                    action
                ]

        # ---------------------------------------------
        # SCREEN ACTIONS
        # ---------------------------------------------

        if intent_type == "screen_action":

            if (
                action == "click_text"
                and
                target
            ):
                return (
                    f"click text {target}"
                )

            if (
                action == "double_click_text"
                and
                target
            ):
                return (
                    f"double click text {target}"
                )

            if (
                action == "right_click_text"
                and
                target
            ):
                return (
                    f"right click text {target}"
                )

            if (
                action == "move_to_text"
                and
                target
            ):
                return (
                    f"move to text {target}"
                )

            if action == "screen_summary":
                return (
                    "what can you see"
                )

            if action == "show_visible_elements":
                return (
                    "show visible elements"
                )

            if action == "show_clickable_elements":
                return (
                    "show clickable elements"
                )

            if (
                action == "where_is"
                and
                target
            ):
                return (
                    f"where is {target}"
                )

        # ---------------------------------------------
        # BROWSER ACTIONS
        # ---------------------------------------------

        if intent_type == "browser_action":

            if (
                action == "open_website"
                and
                target
            ):
                return (
                    f"open website {target}"
                )

            if (
                action == "search_google"
                and
                target
            ):
                return (
                    f"search google for {target}"
                )

            if (
                action == "search_youtube"
                and
                target
            ):
                return (
                    f"search youtube for {target}"
                )

            browser_mapping = {
                "new_tab":
                    "new tab",

                "close_tab":
                    "close tab",

                "next_tab":
                    "next tab",

                "previous_tab":
                    "previous tab",

                "refresh":
                    "refresh page",

                "back":
                    "go back",

                "forward":
                    "go forward",
            }

            if action in browser_mapping:
                return browser_mapping[
                    action
                ]

        # ---------------------------------------------
        # FILE ACTIONS
        # ---------------------------------------------

        if intent_type == "file_action":

            if (
                action == "create_folder"
                and
                target
            ):
                location = str(
                    parameters.get(
                        "location",
                        ""
                    )
                ).strip()

                if location:
                    return (
                        f"create folder {target} "
                        f"in {location}"
                    )

                return (
                    f"create folder {target}"
                )

            if (
                action == "delete_file"
                and
                target
            ):
                return (
                    f"delete file {target}"
                )

            if (
                action == "delete_folder"
                and
                target
            ):
                return (
                    f"delete folder {target}"
                )

        # ---------------------------------------------
        # AUTOMATION ACTIONS
        # ---------------------------------------------

        if intent_type == "automation_action":

            if (
                action == "show_automations"
            ):
                return (
                    "show automations"
                )

            if (
                action == "show_saved_automations"
            ):
                return (
                    "show saved automations"
                )

            if (
                action == "cancel_automation"
                and
                target
            ):
                return (
                    f"cancel automation {target}"
                )

        return None

    # =====================================================
    # EXECUTE STRUCTURED INTENT
    # =====================================================

    def confirmation_for(
        self,
        command,
    ):
        return classify_dangerous_action(
            command
        )

    def execute_command(
        self,
        command,
        intent=None,
    ):
        command = str(
            command
        ).strip()

        if not command:
            return ToolExecutionResult(
                success=False,
                intent=intent,
                error="Command is empty.",
            )

        dangerous_action = (
            self.confirmation_for(
                command
            )
        )

        if dangerous_action is not None:
            return ToolExecutionResult(
                success=False,
                command=command,
                intent=intent,
                error="User confirmation is required.",
                confirmation_required=True,
                dangerous_action=dangerous_action,
            )

        try:
            result = self.command_executor(
                command
            )

        except Exception as error:
            return ToolExecutionResult(
                success=False,
                command=command,
                intent=intent,
                error=(
                    f"Tool execution failed: "
                    f"{error}"
                ),
            )

        return ToolExecutionResult(
            success=True,
            command=command,
            result=result,
            intent=intent,
        )

    def execute(
        self,
        intent
    ):
        command = self.build_command(
            intent
        )

        if not command:
            return ToolExecutionResult(
                success=False,
                intent=intent,
                error=(
                    "No safe WizzArc command mapping "
                    "exists for this intent yet."
                ),
            )

        return self.execute_command(
            command,
            intent=intent,
        )


def create_tool_executor(
    command_executor
):
    return ToolExecutor(
        command_executor
    )