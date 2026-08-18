import re

from brain.command_registry import (
    resolve_registered_command,
)


class CommandRouter:

    # =====================================================
    # NORMALIZE
    # =====================================================

    def normalize(self, text):

        text = (
            str(text)
            .lower()
            .strip()
        )

        text = re.sub(
            r"[.,!?;:]+",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =====================================================
    # CLEAN NATURAL LANGUAGE
    # =====================================================

    def clean_language(
        self,
        text
    ):

        fillers = [
            "please can you",
            "can you please",
            "could you please",
            "would you please",
            "can you",
            "could you",
            "would you",
            "for me",
            "please",
            "mera",
            "meri",
            "mere",
            "mujhe",
            "zara",
        ]

        for filler in fillers:

            text = text.replace(
                filler,
                " "
            )

        replacements = [

            # OPEN
            (
                "khol kar do",
                "open"
            ),
            (
                "open kar do",
                "open"
            ),
            (
                "khol do",
                "open"
            ),
            (
                "khol de",
                "open"
            ),
            (
                "kholna",
                "open"
            ),
            (
                "kholo",
                "open"
            ),
            (
                "khol",
                "open"
            ),

            # START
            (
                "launch karo",
                "open"
            ),
            (
                "launch kar do",
                "open"
            ),
            (
                "start karo",
                "open"
            ),
            (
                "start kar do",
                "open"
            ),

            # VOLUME
            (
                "awaaz",
                "volume"
            ),
            (
                "awaz",
                "volume"
            ),

            # BRIGHTNESS
            (
                "screen light",
                "brightness"
            ),

            # UP
            (
                "tez kar do",
                "up"
            ),
            (
                "tez karo",
                "up"
            ),
            (
                "badha do",
                "up"
            ),
            (
                "badhao",
                "up"
            ),
            (
                "badao",
                "up"
            ),

            # DOWN
            (
                "kam kar do",
                "down"
            ),
            (
                "kam karo",
                "down"
            ),
            (
                "ghata do",
                "down"
            ),

            # Percentage words
            (
                "percentage",
                ""
            ),
            (
                "percent",
                ""
            ),
        ]

        for old, new in replacements:

            text = text.replace(
                old,
                new
            )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =====================================================
    # MAIN ROUTER
    # =====================================================

    def route(
        self,
        text
    ):

        # =============================================
        # ORIGINAL NORMALIZED TEXT
        # =============================================

        original_text = (
            self.normalize(
                text
            )
        )

        if not original_text:
            return ""

        # =============================================
        # REGISTRY FIRST
        #
        # Important:
        # Check original text first because aliases like
        # "chrome band karo" live in registry.
        # =============================================

        result = (
            resolve_registered_command(
                original_text
            )
        )

        if result is not None:

            command = result[
                "command"
            ]

            print(
                "Registry command: "
                f"{original_text} -> {command}"
            )

            return command

        # =============================================
        # CLEAN NATURAL LANGUAGE
        # =============================================

        cleaned_text = (
            self.clean_language(
                original_text
            )
        )

        # =============================================
        # REGISTRY SECOND PASS
        # =============================================

        result = (
            resolve_registered_command(
                cleaned_text
            )
        )

        if result is not None:

            command = result[
                "command"
            ]

            print(
                "Registry cleaned command: "
                f"{cleaned_text} -> {command}"
            )

            return command

        # =============================================
        # FALLBACK
        #
        # Keep unsupported/dynamic text alive.
        # Desktop/System actions can still try it.
        # =============================================

        return cleaned_text