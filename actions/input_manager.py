import pyautogui


# =========================================================
# SETTINGS
# =========================================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


# =========================================================
# PRESS SINGLE KEY
# =========================================================

def press_key(key):

    key = (
        str(key)
        .lower()
        .strip()
    )

    if not key:

        return "Please tell me which key to press."

    aliases = {
        "esc": "escape",
        "return": "enter",
        "spacebar": "space",
        "del": "delete",
    }

    key = aliases.get(
        key,
        key
    )

    try:

        pyautogui.press(
            key
        )

        return (
            f"Pressed {key}."
        )

    except Exception as error:

        return (
            f"Couldn't press {key}: {error}"
        )


# =========================================================
# PRESS HOTKEY
# =========================================================

def press_hotkey(*keys):

    cleaned_keys = []

    aliases = {
        "control": "ctrl",
        "escape": "esc",
        "windows": "win",
        "window": "win",
    }

    for key in keys:

        key = (
            str(key)
            .lower()
            .strip()
        )

        if not key:
            continue

        key = aliases.get(
            key,
            key
        )

        cleaned_keys.append(
            key
        )

    if not cleaned_keys:

        return (
            "Please tell me which shortcut to press."
        )

    try:

        pyautogui.hotkey(
            *cleaned_keys
        )

        return (
            "Pressed "
            + " + ".join(cleaned_keys)
            + "."
        )

    except Exception as error:

        return (
            "Couldn't press shortcut: "
            f"{error}"
        )


# =========================================================
# TYPE TEXT
# =========================================================

def type_text(
    text
):

    text = str(
        text
    )

    if not text:

        return (
            "Please tell me what to type."
        )

    try:

        pyautogui.write(
            text,
            interval=0.02
        )

        return (
            f"Typed: {text}"
        )

    except Exception as error:

        return (
            f"Couldn't type text: {error}"
        )


# =========================================================
# CLICK
# =========================================================

def left_click():

    try:

        pyautogui.click()

        return (
            "Mouse clicked."
        )

    except Exception as error:

        return (
            f"Couldn't click mouse: {error}"
        )


# =========================================================
# DOUBLE CLICK
# =========================================================

def double_click():

    try:

        pyautogui.doubleClick(
            interval=0.15
        )

        return (
            "Mouse double-clicked."
        )

    except Exception as error:

        return (
            f"Couldn't double-click: {error}"
        )


# =========================================================
# RIGHT CLICK
# =========================================================

def right_click():

    try:

        pyautogui.rightClick()

        return (
            "Mouse right-clicked."
        )

    except Exception as error:

        return (
            f"Couldn't right-click: {error}"
        )


# =========================================================
# SCROLL
# =========================================================

def scroll_up(
    amount=5
):

    try:

        amount = int(
            amount
        )

        amount = max(
            1,
            abs(amount)
        )

        pyautogui.scroll(
            amount
        )

        return (
            f"Scrolled up {amount}."
        )

    except Exception as error:

        return (
            f"Couldn't scroll up: {error}"
        )


def scroll_down(
    amount=5
):

    try:

        amount = int(
            amount
        )

        amount = max(
            1,
            abs(amount)
        )

        pyautogui.scroll(
            -amount
        )

        return (
            f"Scrolled down {amount}."
        )

    except Exception as error:

        return (
            f"Couldn't scroll down: {error}"
        )


# =========================================================
# MOVE MOUSE
# =========================================================

def move_mouse(
    x,
    y
):

    try:

        x = int(
            x
        )

        y = int(
            y
        )

    except ValueError:

        return (
            "Mouse coordinates must be numbers."
        )

    screen_width, screen_height = (
        pyautogui.size()
    )

    if (
        x < 0
        or y < 0
        or x >= screen_width
        or y >= screen_height
    ):

        return (
            f"Coordinates are outside the screen. "
            f"Screen size is "
            f"{screen_width}x{screen_height}."
        )

    try:

        pyautogui.moveTo(
            x,
            y,
            duration=0.2
        )

        return (
            f"Mouse moved to {x}, {y}."
        )

    except Exception as error:

        return (
            f"Couldn't move mouse: {error}"
        )


# =========================================================
# CLICK AT POSITION
# =========================================================

def click_at(
    x,
    y
):

    result = move_mouse(
        x,
        y
    )

    if not result.startswith(
        "Mouse moved"
    ):

        return result

    try:

        pyautogui.click()

        return (
            f"Clicked at {x}, {y}."
        )

    except Exception as error:

        return (
            f"Couldn't click: {error}"
        )


# =========================================================
# CURRENT MOUSE POSITION
# =========================================================

def get_mouse_position():

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
    