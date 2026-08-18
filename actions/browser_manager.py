import re
import webbrowser

import pyautogui


# =========================================================
# NORMALIZE WEBSITE
# =========================================================

def normalize_website(
    website
):

    website = (
        str(website)
        .strip()
    )

    if not website:

        return None

    if not re.match(
        r"^https?://",
        website,
        re.IGNORECASE
    ):

        website = (
            "https://"
            + website
        )

    return website


# =========================================================
# OPEN WEBSITE
# =========================================================

def open_website(
    website
):

    website = normalize_website(
        website
    )

    if not website:

        return (
            "Please tell me which "
            "website to open."
        )

    try:

        webbrowser.open(
            website
        )

        return (
            f"Opening {website}."
        )

    except Exception as error:

        return (
            f"Couldn't open website: "
            f"{error}"
        )


# =========================================================
# GOOGLE SEARCH
# =========================================================

def search_google(
    query
):

    query = (
        str(query)
        .strip()
    )

    if not query:

        return (
            "Please tell me what "
            "to search on Google."
        )

    try:

        search_url = (
            "https://www.google.com/search?q="
            + query.replace(
                " ",
                "+"
            )
        )

        webbrowser.open(
            search_url
        )

        return (
            f"Searching Google for "
            f"{query}."
        )

    except Exception as error:

        return (
            f"Couldn't search Google: "
            f"{error}"
        )


# =========================================================
# YOUTUBE SEARCH
# =========================================================

def search_youtube(
    query
):

    query = (
        str(query)
        .strip()
    )

    if not query:

        return (
            "Please tell me what "
            "to search on YouTube."
        )

    try:

        search_url = (
            "https://www.youtube.com/results"
            "?search_query="
            + query.replace(
                " ",
                "+"
            )
        )

        webbrowser.open(
            search_url
        )

        return (
            f"Searching YouTube for "
            f"{query}."
        )

    except Exception as error:

        return (
            f"Couldn't search YouTube: "
            f"{error}"
        )


# =========================================================
# NEW TAB
# =========================================================

def new_tab():

    try:

        pyautogui.hotkey(
            "ctrl",
            "t"
        )

        return (
            "Opened a new tab."
        )

    except Exception as error:

        return (
            f"Couldn't open new tab: "
            f"{error}"
        )


# =========================================================
# CLOSE TAB
# =========================================================

def close_tab():

    try:

        pyautogui.hotkey(
            "ctrl",
            "w"
        )

        return (
            "Closed current tab."
        )

    except Exception as error:

        return (
            f"Couldn't close tab: "
            f"{error}"
        )


# =========================================================
# NEXT TAB
# =========================================================

def next_tab():

    try:

        pyautogui.hotkey(
            "ctrl",
            "tab"
        )

        return (
            "Switched to next tab."
        )

    except Exception as error:

        return (
            f"Couldn't switch tab: "
            f"{error}"
        )


# =========================================================
# PREVIOUS TAB
# =========================================================

def previous_tab():

    try:

        pyautogui.hotkey(
            "ctrl",
            "shift",
            "tab"
        )

        return (
            "Switched to previous tab."
        )

    except Exception as error:

        return (
            f"Couldn't switch tab: "
            f"{error}"
        )


# =========================================================
# REFRESH PAGE
# =========================================================

def refresh_page():

    try:

        pyautogui.hotkey(
            "ctrl",
            "r"
        )

        return (
            "Page refreshed."
        )

    except Exception as error:

        return (
            f"Couldn't refresh page: "
            f"{error}"
        )


# =========================================================
# GO BACK
# =========================================================

def go_back():

    try:

        pyautogui.hotkey(
            "alt",
            "left"
        )

        return (
            "Going back."
        )

    except Exception as error:

        return (
            f"Couldn't go back: "
            f"{error}"
        )


# =========================================================
# GO FORWARD
# =========================================================

def go_forward():

    try:

        pyautogui.hotkey(
            "alt",
            "right"
        )

        return (
            "Going forward."
        )

    except Exception as error:

        return (
            f"Couldn't go forward: "
            f"{error}"
        )


# =========================================================
# FOCUS ADDRESS BAR
# =========================================================

def focus_address_bar():

    try:

        pyautogui.hotkey(
            "ctrl",
            "l"
        )

        return (
            "Address bar focused."
        )

    except Exception as error:

        return (
            f"Couldn't focus address bar: "
            f"{error}"
        )