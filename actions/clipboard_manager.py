import os
from pathlib import Path

import pyperclip
import pyautogui


# =========================================================
# COPY TEXT TO CLIPBOARD
# =========================================================

def copy_text_to_clipboard(text):

    text = str(text)

    if not text:

        return "Please tell me what text to copy."

    try:

        pyperclip.copy(text)

        return (
            f"Copied to clipboard: {text}"
        )

    except Exception as error:

        return (
            f"Couldn't copy text to clipboard: {error}"
        )


# =========================================================
# READ CLIPBOARD
# =========================================================

def get_clipboard_text():

    try:

        text = pyperclip.paste()

        if not text:

            return "Clipboard is empty."

        return (
            f"Clipboard: {text}"
        )

    except Exception as error:

        return (
            f"Couldn't read clipboard: {error}"
        )


# =========================================================
# CLEAR CLIPBOARD
# =========================================================

def clear_clipboard():

    try:

        pyperclip.copy("")

        return (
            "Clipboard cleared."
        )

    except Exception as error:

        return (
            f"Couldn't clear clipboard: {error}"
        )


# =========================================================
# PASTE CLIPBOARD
# =========================================================

def paste_clipboard():

    try:

        text = pyperclip.paste()

        if not text:

            return (
                "Clipboard is empty."
            )

        pyautogui.hotkey(
            "ctrl",
            "v"
        )

        return (
            "Clipboard pasted."
        )

    except Exception as error:

        return (
            f"Couldn't paste clipboard: {error}"
        )


# =========================================================
# SAVE CLIPBOARD TO FILE
# =========================================================

def save_clipboard_to_file(
    filename="clipboard.txt",
    location="documents"
):

    try:

        text = pyperclip.paste()

    except Exception as error:

        return (
            f"Couldn't read clipboard: {error}"
        )

    if not text:

        return (
            "Clipboard is empty."
        )

    home = Path.home()

    locations = {
        "desktop":
            home / "Desktop",

        "documents":
            home / "Documents",

        "downloads":
            home / "Downloads",
    }

    location = (
        str(location)
        .lower()
        .strip()
    )

    if location not in locations:

        return (
            f"Unknown location: {location}"
        )

    base = locations[
        location
    ]

    if not base.exists():

        return (
            f"{location.title()} folder "
            "was not found."
        )

    filename = (
        str(filename)
        .strip()
    )

    if not filename:

        filename = "clipboard.txt"

    if "." not in filename:

        filename += ".txt"

    target = (
        base
        / filename
    )

    try:

        target.write_text(
            text,
            encoding="utf-8"
        )

        return (
            f"Clipboard saved to "
            f"{target}."
        )

    except PermissionError:

        return (
            "WizzArc doesn't have permission "
            "to save the clipboard there."
        )

    except Exception as error:

        return (
            f"Couldn't save clipboard: {error}"
        )


# =========================================================
# COPY SELECTED TEXT
# =========================================================

def copy_selected_text():

    try:

        pyautogui.hotkey(
            "ctrl",
            "c"
        )

        return (
            "Selected text copied."
        )

    except Exception as error:

        return (
            f"Couldn't copy selected text: {error}"
        )
