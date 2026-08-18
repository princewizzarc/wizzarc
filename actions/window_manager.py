import pygetwindow as gw


# =========================================================
# NORMALIZE
# =========================================================

def normalize_title(text):

    return (
        str(text)
        .lower()
        .strip()
    )


# =========================================================
# FIND WINDOW
# =========================================================

def find_window(
    name
):

    name = normalize_title(
        name
    )

    if not name:
        return None

    windows = gw.getAllWindows()

    partial_match = None

    for window in windows:

        try:

            title = normalize_title(
                window.title
            )

            if not title:
                continue

            # Exact title
            if title == name:
                return window

            # App/title contained
            if (
                name in title
                and partial_match is None
            ):

                partial_match = window

        except Exception:
            continue

    return partial_match


# =========================================================
# MINIMIZE WINDOW
# =========================================================

def minimize_window(
    name
):

    window = find_window(
        name
    )

    if not window:

        return (
            f"I couldn't find an open window "
            f"called '{name}'."
        )

    try:

        window.minimize()

        return (
            f"{name.title()} minimized."
        )

    except Exception as error:

        return (
            f"Couldn't minimize "
            f"{name}: {error}"
        )


# =========================================================
# MAXIMIZE WINDOW
# =========================================================

def maximize_window(
    name
):

    window = find_window(
        name
    )

    if not window:

        return (
            f"I couldn't find an open window "
            f"called '{name}'."
        )

    try:

        window.maximize()

        return (
            f"{name.title()} maximized."
        )

    except Exception as error:

        return (
            f"Couldn't maximize "
            f"{name}: {error}"
        )


# =========================================================
# RESTORE WINDOW
# =========================================================

def restore_window(
    name
):

    window = find_window(
        name
    )

    if not window:

        return (
            f"I couldn't find an open window "
            f"called '{name}'."
        )

    try:

        window.restore()

        return (
            f"{name.title()} restored."
        )

    except Exception as error:

        return (
            f"Couldn't restore "
            f"{name}: {error}"
        )


# =========================================================
# SWITCH / FOCUS WINDOW
# =========================================================

def switch_to_window(
    name
):

    window = find_window(
        name
    )

    if not window:

        return (
            f"I couldn't find an open window "
            f"called '{name}'."
        )

    try:

        if window.isMinimized:

            window.restore()

        window.activate()

        return (
            f"Switched to {name.title()}."
        )

    except Exception as error:

        return (
            f"Couldn't switch to "
            f"{name}: {error}"
        )


# =========================================================
# CLOSE WINDOW
# =========================================================

def close_window(
    name
):

    window = find_window(
        name
    )

    if not window:

        return (
            f"I couldn't find an open window "
            f"called '{name}'."
        )

    try:

        window.close()

        return (
            f"{name.title()} window closed."
        )

    except Exception as error:

        return (
            f"Couldn't close "
            f"{name}: {error}"
        )


# =========================================================
# GET ACTIVE WINDOW
# =========================================================

def get_active_window():

    try:

        return gw.getActiveWindow()

    except Exception:

        return None


# =========================================================
# MINIMIZE CURRENT WINDOW
# =========================================================

def minimize_current_window():

    window = get_active_window()

    if not window:

        return (
            "I couldn't detect the current window."
        )

    try:

        window.minimize()

        return (
            "Current window minimized."
        )

    except Exception as error:

        return (
            f"Couldn't minimize current window: "
            f"{error}"
        )


# =========================================================
# MAXIMIZE CURRENT WINDOW
# =========================================================

def maximize_current_window():

    window = get_active_window()

    if not window:

        return (
            "I couldn't detect the current window."
        )

    try:

        window.maximize()

        return (
            "Current window maximized."
        )

    except Exception as error:

        return (
            f"Couldn't maximize current window: "
            f"{error}"
        )


# =========================================================
# RESTORE CURRENT WINDOW
# =========================================================

def restore_current_window():

    window = get_active_window()

    if not window:

        return (
            "I couldn't detect the current window."
        )

    try:

        window.restore()

        return (
            "Current window restored."
        )

    except Exception as error:

        return (
            f"Couldn't restore current window: "
            f"{error}"
        )


# =========================================================
# CLOSE CURRENT WINDOW
# =========================================================

def close_current_window():

    window = get_active_window()

    if not window:

        return (
            "I couldn't detect the current window."
        )

    try:

        window.close()

        return (
            "Current window closed."
        )

    except Exception as error:

        return (
            f"Couldn't close current window: "
            f"{error}"
        )


# =========================================================
# LIST OPEN WINDOWS
# =========================================================

def list_open_windows():

    titles = []

    try:

        for window in gw.getAllWindows():

            title = (
                str(window.title)
                .strip()
            )

            if (
                title
                and title not in titles
            ):

                titles.append(
                    title
                )

    except Exception as error:

        return (
            f"Couldn't read open windows: "
            f"{error}"
        )

    if not titles:

        return (
            "No open windows found."
        )

    lines = [
        "Open windows:"
    ]

    for title in titles:

        lines.append(
            f"- {title}"
        )

    return "\n".join(
        lines
    )