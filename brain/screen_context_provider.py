from dataclasses import dataclass
from typing import Optional

from actions.screen_understanding import (
    ensure_screen_snapshot,
    get_screen_context_summary,
    get_screen_summary,
    get_screen_snapshot_status,
)


@dataclass
class ScreenContext:
    available: bool
    summary: str = ""
    regions: str = ""
    snapshot_status: str = ""
    error: Optional[str] = None

    def to_prompt_context(self):
        if not self.available:
            return "Current screen context is unavailable."

        parts = ["CURRENT SCREEN CONTEXT:"]

        if self.summary:
            parts.extend(["", "Screen summary:", self.summary])

        if self.regions:
            parts.extend(["", "Screen regions:", self.regions])

        if self.snapshot_status:
            parts.extend(["", "Snapshot status:", self.snapshot_status])

        return "\n".join(parts)


class ScreenContextProvider:

    def __init__(self, refresh=False):
        self.refresh = refresh

    def get_context(self, refresh=None):
        if refresh is None:
            refresh = self.refresh

        try:
            try:
                ensure_screen_snapshot(
                    force_refresh=bool(refresh)
                )
            except TypeError:
                ensure_screen_snapshot()

            return ScreenContext(
                available=True,
                summary=str(
                    get_screen_summary()
                ).strip(),
                regions=str(
                    get_screen_context_summary()
                ).strip(),
                snapshot_status=str(
                    get_screen_snapshot_status()
                ).strip(),
            )

        except Exception as error:
            return ScreenContext(
                available=False,
                error=str(error),
            )


def create_screen_context_provider(refresh=False):
    return ScreenContextProvider(refresh=refresh)