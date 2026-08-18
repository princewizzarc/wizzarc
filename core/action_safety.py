from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class DangerousAction:
    kind: str
    command: str
    target: str = ""
    title: str = ""
    message: str = ""


class ConfirmationRequired(RuntimeError):

    def __init__(
        self,
        action: DangerousAction,
    ):
        self.action = action

        super().__init__(
            f"Confirmation required: "
            f"{action.kind}: {action.command}"
        )


def normalize_command(
    command,
):
    return " ".join(
        str(command)
        .strip()
        .lower()
        .split()
    )


def classify_dangerous_action(
    command,
) -> Optional[DangerousAction]:

    command = normalize_command(
        command
    )

    if not command:
        return None

    # -------------------------------------------------
    # POWER ACTIONS
    # -------------------------------------------------

    if command in {
        "shutdown",
        "shut down",
        "shutdown computer",
        "shutdown pc",
        "shut down computer",
        "shut down pc",
    }:
        return DangerousAction(
            kind="shutdown",
            command=command,
            title="Confirm Shutdown",
            message=(
                "Are you sure you want to "
                "shut down this computer?"
            ),
        )

    if command in {
        "restart",
        "restart computer",
        "restart pc",
        "reboot",
        "reboot computer",
        "reboot pc",
    }:
        return DangerousAction(
            kind="restart",
            command=command,
            title="Confirm Restart",
            message=(
                "Are you sure you want to "
                "restart this computer?"
            ),
        )

    # -------------------------------------------------
    # FILE / FOLDER DELETE
    # -------------------------------------------------

    delete_match = re.fullmatch(
        r"(?:delete|remove)\s+"
        r"(?:(file|folder)\s+)?"
        r"(.+)",
        command,
    )

    if delete_match:
        item_type = (
            delete_match.group(1)
            or "item"
        )

        target = (
            delete_match.group(2)
            .strip()
        )

        # Avoid treating harmless phrases with no real target
        # as an executable destructive action.
        if target:
            return DangerousAction(
                kind="delete",
                command=command,
                target=target,
                title="Confirm Delete",
                message=(
                    f"Move '{target}' "
                    "to Recycle Bin?"
                ),
            )

    return None


def requires_confirmation(
    command,
):
    return (
        classify_dangerous_action(
            command
        )
        is not None
    )


def guard_command(
    command,
):
    """
    Return normalized safe command.

    Dangerous commands are NEVER executed here.
    Instead, ConfirmationRequired is raised so the UI layer
    can ask the user before calling the real executor.
    """

    normalized = normalize_command(
        command
    )

    action = classify_dangerous_action(
        normalized
    )

    if action is not None:
        raise ConfirmationRequired(
            action
        )

    return normalized


def execute_guarded(
    command,
    executor,
):
    """
    Convenience wrapper used by tests/integration.

    Safe commands reach executor.
    Dangerous commands raise ConfirmationRequired BEFORE
    executor can be called.
    """

    if not callable(
        executor
    ):
        raise TypeError(
            "executor must be callable."
        )

    safe_command = guard_command(
        command
    )

    return executor(
        safe_command
    )