from actions.desktop_actions import execute_command as legacy_execute_command
from brain.custom_app_manager import CUSTOM_APP_MANAGER


# =========================================================
# CUSTOM + LEGACY COMMAND EXECUTOR
# =========================================================

def execute_wizzarc_command(
    command
):

    command = (
        str(command)
        .strip()
    )

    if not command:

        return (
            "Please enter a command."
        )

    # =====================================================
    # IMPROVEMENT #8 - CUSTOM APP EXACT COMMAND / ALIAS
    # =====================================================

    custom_app = (
        CUSTOM_APP_MANAGER
        .resolve_command(
            command
        )
    )

    if custom_app is not None:

        result = (
            CUSTOM_APP_MANAGER
            .open_app(
                custom_app
            )
        )

        if result is not None:
            return result

    # =====================================================
    # IMPROVEMENT #8 - AI NORMALIZED OPEN COMMAND
    # Example:
    #   user: "can you launch pycharm"
    #   AI tool command: "open pycharm"
    # =====================================================

    lower = (
        command
        .lower()
        .strip()
    )

    if lower.startswith(
        "open "
    ):

        target = command[
            len("open "):
        ].strip()

        result = (
            CUSTOM_APP_MANAGER
            .open_app(
                target
            )
        )

        if result is not None:
            return result

    # =====================================================
    # IMPROVEMENT #8 - CUSTOM APP CLOSE
    # =====================================================

    if lower.startswith(
        "close "
    ):

        target = command[
            len("close "):
        ].strip()

        result = (
            CUSTOM_APP_MANAGER
            .close_app(
                target
            )
        )

        if result is not None:
            return result

    # =====================================================
    # FALLBACK TO EXISTING WIZZARC COMMAND SYSTEM
    # =====================================================

    return legacy_execute_command(
        command
    )