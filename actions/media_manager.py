import pyautogui


# =========================================================
# SETTINGS
# =========================================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


# =========================================================
# PLAY / PAUSE
# =========================================================

def play_pause_media():

    try:

        pyautogui.press(
            "playpause"
        )

        return (
            "Media play/pause toggled."
        )

    except Exception as error:

        return (
            f"Couldn't control media: {error}"
        )


# =========================================================
# PLAY MEDIA
# =========================================================

def play_media():

    # Windows media key works as toggle.
    # At command level we expose a natural "play media"
    # command even though the hardware signal is play/pause.

    try:

        pyautogui.press(
            "playpause"
        )

        return (
            "Media playback toggled."
        )

    except Exception as error:

        return (
            f"Couldn't play media: {error}"
        )


# =========================================================
# PAUSE MEDIA
# =========================================================

def pause_media():

    try:

        pyautogui.press(
            "playpause"
        )

        return (
            "Media playback toggled."
        )

    except Exception as error:

        return (
            f"Couldn't pause media: {error}"
        )


# =========================================================
# NEXT TRACK
# =========================================================

def next_track():

    try:

        pyautogui.press(
            "nexttrack"
        )

        return (
            "Skipping to next track."
        )

    except Exception as error:

        return (
            f"Couldn't skip track: {error}"
        )


# =========================================================
# PREVIOUS TRACK
# =========================================================

def previous_track():

    try:

        pyautogui.press(
            "prevtrack"
        )

        return (
            "Going to previous track."
        )

    except Exception as error:

        return (
            f"Couldn't go to previous track: "
            f"{error}"
        )


# =========================================================
# STOP MEDIA
# =========================================================

def stop_media():

    try:

        pyautogui.press(
            "stop"
        )

        return (
            "Media stopped."
        )

    except Exception as error:

        return (
            f"Couldn't stop media: {error}"
        )