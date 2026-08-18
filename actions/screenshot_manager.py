import os
from datetime import datetime
from pathlib import Path

import pyautogui


# =========================================================
# SCREENSHOT FOLDER
# =========================================================

def get_screenshot_folder():

    pictures = (
        Path.home()
        / "Pictures"
    )

    target = (
        pictures
        / "WizzArc Screenshots"
    )

    try:
        target.mkdir(
            parents=True,
            exist_ok=True
        )

    except Exception:
        pass

    return target


# =========================================================
# SAFE FILE NAME
# =========================================================

def make_safe_filename(
    name
):

    name = (
        str(name)
        .strip()
    )

    if not name:

        return None

    invalid_chars = '<>:"/\\|?*'

    for char in invalid_chars:
        name = name.replace(
            char,
            "_"
        )

    if not name.lower().endswith(
        ".png"
    ):
        name += ".png"

    return name


# =========================================================
# AUTO SCREENSHOT NAME
# =========================================================

def generate_screenshot_name():

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    return (
        f"WizzArc_{timestamp}.png"
    )


# =========================================================
# TAKE SCREENSHOT
# =========================================================

def take_screenshot(
    filename=None
):

    folder = (
        get_screenshot_folder()
    )

    if filename:

        filename = make_safe_filename(
            filename
        )

        if not filename:

            return (
                "Invalid screenshot name."
            )

    else:

        filename = (
            generate_screenshot_name()
        )

    target = (
        folder
        / filename
    )

    # Avoid overwriting
    if target.exists():

        stem = target.stem
        suffix = target.suffix

        counter = 2

        while target.exists():

            target = (
                folder
                / f"{stem}_{counter}{suffix}"
            )

            counter += 1

    try:

        image = (
            pyautogui.screenshot()
        )

        image.save(
            str(target)
        )

        return (
            f"Screenshot saved to "
            f"{target}."
        )

    except PermissionError:

        return (
            "WizzArc doesn't have permission "
            "to save the screenshot."
        )

    except Exception as error:

        return (
            f"Couldn't take screenshot: "
            f"{error}"
        )


# =========================================================
# OPEN SCREENSHOT FOLDER
# =========================================================

def open_screenshot_folder():

    folder = (
        get_screenshot_folder()
    )

    if not folder.exists():

        return (
            "Screenshot folder was not found."
        )

    try:

        os.startfile(
            str(folder)
        )

        return (
            "Screenshot folder opened."
        )

    except Exception as error:

        return (
            f"Couldn't open screenshot folder: "
            f"{error}"
        )


# =========================================================
# SCREEN SIZE
# =========================================================

def get_screen_size():

    try:

        width, height = (
            pyautogui.size()
        )

        return (
            f"Screen size is "
            f"{width} by {height}."
        )

    except Exception as error:

        return (
            f"Couldn't read screen size: "
            f"{error}"
        )


# =========================================================
# MOUSE POSITION
# =========================================================

def get_current_mouse_position():

    try:

        x, y = (
            pyautogui.position()
        )

        return (
            f"Mouse position is "
            f"{x}, {y}."
        )

    except Exception as error:

        return (
            f"Couldn't read mouse position: "
            f"{error}"
        )