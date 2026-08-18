import ctypes
import subprocess
import re
import time
import os
from datetime import datetime
from pathlib import Path

import pyautogui
import screen_brightness_control as sbc


# =========================================================
# WINDOWS MEDIA KEYS
# =========================================================

VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

KEYEVENTF_KEYUP = 0x0002


def press_media_key(key_code, presses=1):
    for _ in range(presses):
        ctypes.windll.user32.keybd_event(
            key_code,
            0,
            0,
            0
        )

        ctypes.windll.user32.keybd_event(
            key_code,
            0,
            KEYEVENTF_KEYUP,
            0
        )

        time.sleep(0.01)


# =========================================================
# VOLUME
# =========================================================

def volume_up():
    try:
        press_media_key(VK_VOLUME_UP, 2)
        return "Volume increased."

    except Exception as error:
        return f"Couldn't increase volume: {error}"


def volume_down():
    try:
        press_media_key(VK_VOLUME_DOWN, 2)
        return "Volume decreased."

    except Exception as error:
        return f"Couldn't decrease volume: {error}"


def set_volume(percent):
    try:
        percent = int(percent)
        percent = max(0, min(100, percent))

        # First bring volume down to minimum.
        press_media_key(
            VK_VOLUME_DOWN,
            60
        )

        # Windows generally changes volume by roughly 2%
        # per multimedia key press.
        required_presses = round(
            percent / 2
        )

        if required_presses > 0:
            press_media_key(
                VK_VOLUME_UP,
                required_presses
            )

        return (
            f"Volume set to approximately {percent}%."
        )

    except Exception as error:
        return f"Couldn't set volume: {error}"


# =========================================================
# MUTE / UNMUTE
# =========================================================

def mute_volume():
    try:
        press_media_key(VK_VOLUME_MUTE)
        return "Mute toggled."

    except Exception as error:
        return f"Couldn't mute volume: {error}"


def unmute_volume():
    try:
        press_media_key(VK_VOLUME_MUTE)
        return "Mute toggled."

    except Exception as error:
        return f"Couldn't unmute volume: {error}"


# =========================================================
# BRIGHTNESS
# =========================================================

def set_brightness(percent):
    try:
        percent = int(percent)
        percent = max(0, min(100, percent))

        sbc.set_brightness(percent)

        return f"Brightness set to {percent}%."

    except Exception as error:
        return f"Couldn't set brightness: {error}"


def brightness_up():
    try:
        values = sbc.get_brightness()

        if not values:
            return "Couldn't read brightness."

        current = values[0]

        new_value = min(
            100,
            current + 10
        )

        sbc.set_brightness(
            new_value
        )

        return (
            f"Brightness increased to {new_value}%."
        )

    except Exception as error:
        return f"Couldn't increase brightness: {error}"


def brightness_down():
    try:
        values = sbc.get_brightness()

        if not values:
            return "Couldn't read brightness."

        current = values[0]

        new_value = max(
            0,
            current - 10
        )

        sbc.set_brightness(
            new_value
        )

        return (
            f"Brightness decreased to {new_value}%."
        )

    except Exception as error:
        return f"Couldn't decrease brightness: {error}"


# =========================================================
# SCREENSHOT
# =========================================================

def take_screenshot():
    try:
        screenshots_folder = (
            Path.home()
            / "Pictures"
            / "WizzArc Screenshots"
        )

        screenshots_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        file_path = (
            screenshots_folder
            / f"WizzArc_{timestamp}.png"
        )

        screenshot = pyautogui.screenshot()

        screenshot.save(
            file_path
        )

        return (
            f"Screenshot saved: {file_path}"
        )

    except Exception as error:
        return f"Couldn't take screenshot: {error}"


# =========================================================
# WINDOWS SETTINGS
# =========================================================

def open_windows_setting(uri, name):
    try:
        os.startfile(uri)

        return f"{name} opened."

    except Exception as error:
        return f"Couldn't open {name}: {error}"


def open_wifi_settings():
    return open_windows_setting(
        "ms-settings:network-wifi",
        "Wi-Fi settings"
    )


def open_bluetooth_settings():
    return open_windows_setting(
        "ms-settings:bluetooth",
        "Bluetooth settings"
    )


def open_network_settings():
    return open_windows_setting(
        "ms-settings:network-status",
        "Network settings"
    )


def open_sound_settings():
    return open_windows_setting(
        "ms-settings:sound",
        "Sound settings"
    )


def open_display_settings():
    return open_windows_setting(
        "ms-settings:display",
        "Display settings"
    )


# =========================================================
# WIFI
# =========================================================

def find_wifi_adapter():
    try:
        result = subprocess.run(
            [
                "netsh",
                "interface",
                "show",
                "interface"
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        output = result.stdout

        for line in output.splitlines():
            line_lower = line.lower()

            if (
                "wi-fi" in line_lower
                or "wifi" in line_lower
                or "wireless" in line_lower
                or "wlan" in line_lower
            ):
                parts = line.split()

                if len(parts) >= 4:
                    return " ".join(
                        parts[3:]
                    )

        return "Wi-Fi"

    except Exception:
        return "Wi-Fi"


def set_wifi(enabled):
    try:
        adapter = find_wifi_adapter()

        state = (
            "enabled"
            if enabled
            else "disabled"
        )

        result = subprocess.run(
            [
                "netsh",
                "interface",
                "set",
                "interface",
                f"name={adapter}",
                f"admin={state}"
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        response = (
            result.stderr
            or result.stdout
            or ""
        ).strip()

        if result.returncode != 0:
            return (
                "Wi-Fi control needs Administrator "
                f"permission. Windows response: {response}"
            )

        if enabled:
            return "Wi-Fi turned on."

        return "Wi-Fi turned off."

    except Exception as error:
        return f"Couldn't control Wi-Fi: {error}"


# =========================================================
# BLUETOOTH
# =========================================================

BLUETOOTH_ADAPTER = "MediaTek Bluetooth Adapter"


def set_bluetooth(enabled):
    """
    Enable/disable the laptop's Bluetooth adapter.

    This operation normally requires WizzArc to be running
    with Administrator privileges.
    """

    try:
        action = (
            "Enable-PnpDevice"
            if enabled
            else "Disable-PnpDevice"
        )

        # Escape apostrophes in case an adapter name ever
        # contains one.
        safe_adapter_name = BLUETOOTH_ADAPTER.replace(
            "'",
            "''"
        )

        powershell_command = (
            "Get-PnpDevice -Class Bluetooth | "
            "Where-Object {"
            f"$_.FriendlyName -eq '{safe_adapter_name}'"
            "} | "
            f"{action} -Confirm:$false"
        )

        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                powershell_command
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        error_text = (
            result.stderr
            or ""
        ).strip()

        if result.returncode != 0:
            return (
                "Bluetooth control failed. "
                "Run WizzArc as Administrator. "
                f"Windows response: {error_text}"
            )

        # Check that the adapter actually existed.
        check_command = (
            "Get-PnpDevice -Class Bluetooth | "
            "Where-Object {"
            f"$_.FriendlyName -eq '{safe_adapter_name}'"
            "} | "
            "Select-Object -ExpandProperty FriendlyName"
        )

        check_result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                check_command
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if BLUETOOTH_ADAPTER.lower() not in (
            check_result.stdout.lower()
        ):
            return (
                f"Bluetooth adapter "
                f"'{BLUETOOTH_ADAPTER}' was not found."
            )

        if enabled:
            return "Bluetooth turned on."

        return "Bluetooth turned off."

    except Exception as error:
        return (
            f"Couldn't control Bluetooth: {error}"
        )


# =========================================================
# LOCK COMPUTER
# =========================================================

def lock_computer():
    try:
        ctypes.windll.user32.LockWorkStation()

        return "Computer locked."

    except Exception as error:
        return f"Couldn't lock computer: {error}"


# =========================================================
# POWER ACTION DETECTION
# =========================================================

def prepare_power_action(command):
    command = command.strip().lower()

    shutdown_commands = [
        "shutdown",
        "shutdown computer",
        "shutdown pc",
        "turn off computer",
        "turn off pc",
    ]

    restart_commands = [
        "restart",
        "restart computer",
        "restart pc",
        "reboot",
        "reboot computer",
    ]

    if command in shutdown_commands:
        return "shutdown"

    if command in restart_commands:
        return "restart"

    return None


# =========================================================
# POWER ACTION
# =========================================================

def perform_power_action(action):
    try:
        if action == "shutdown":
            subprocess.Popen(
                [
                    "shutdown.exe",
                    "/s",
                    "/t",
                    "0"
                ]
            )

            return "Shutting down computer."

        if action == "restart":
            subprocess.Popen(
                [
                    "shutdown.exe",
                    "/r",
                    "/t",
                    "0"
                ]
            )

            return "Restarting computer."

        return "Unknown power action."

    except Exception as error:
        return f"Power action failed: {error}"


# =========================================================
# SYSTEM COMMAND ENGINE
# =========================================================

def execute_system_command(command):
    command = command.strip().lower()

    # =====================================================
    # EXACT VOLUME
    # =====================================================

    volume_patterns = [
        r"set volume(?: to)? (\d{1,3})%?",
        r"volume (\d{1,3})%?",
    ]

    for pattern in volume_patterns:
        match = re.fullmatch(
            pattern,
            command
        )

        if match:
            return set_volume(
                match.group(1)
            )

    # =====================================================
    # EXACT BRIGHTNESS
    # =====================================================

    brightness_patterns = [
        r"set brightness(?: to)? (\d{1,3})%?",
        r"brightness (\d{1,3})%?",
    ]

    for pattern in brightness_patterns:
        match = re.fullmatch(
            pattern,
            command
        )

        if match:
            return set_brightness(
                match.group(1)
            )

    # =====================================================
    # VOLUME
    # =====================================================

    if command in [
        "volume up",
        "increase volume",
        "turn volume up",
        "volume badhao",
        "volume badha do",
    ]:
        return volume_up()

    if command in [
        "volume down",
        "decrease volume",
        "turn volume down",
        "volume kam karo",
        "volume kam kar do",
    ]:
        return volume_down()

    if command in [
        "mute",
        "mute volume",
        "sound off",
        "volume mute",
    ]:
        return mute_volume()

    if command in [
        "unmute",
        "unmute volume",
        "sound on",
        "volume unmute",
    ]:
        return unmute_volume()

    # =====================================================
    # BRIGHTNESS
    # =====================================================

    if command in [
        "brightness up",
        "increase brightness",
        "brightness badhao",
        "brightness badha do",
    ]:
        return brightness_up()

    if command in [
        "brightness down",
        "decrease brightness",
        "brightness kam karo",
        "brightness kam kar do",
    ]:
        return brightness_down()

    # =====================================================
    # SCREENSHOT
    # =====================================================

    if command in [
        "take screenshot",
        "screenshot",
        "capture screen",
        "screen shot lo",
        "screenshot lo",
    ]:
        return take_screenshot()

    # =====================================================
    # WIFI
    # =====================================================

    if command in [
        "wifi on",
        "wi-fi on",
        "turn on wifi",
        "turn wifi on",
        "wifi chalu karo",
    ]:
        return set_wifi(True)

    if command in [
        "wifi off",
        "wi-fi off",
        "turn off wifi",
        "turn wifi off",
        "wifi band karo",
    ]:
        return set_wifi(False)

    # =====================================================
    # BLUETOOTH
    # =====================================================

    if command in [
        "bluetooth on",
        "turn on bluetooth",
        "turn bluetooth on",
        "bluetooth chalu karo",
    ]:
        return set_bluetooth(True)

    if command in [
        "bluetooth off",
        "turn off bluetooth",
        "turn bluetooth off",
        "bluetooth band karo",
    ]:
        return set_bluetooth(False)

    # =====================================================
    # WINDOWS SETTINGS
    # =====================================================

    if command in [
        "open wifi settings",
        "open wi-fi settings",
        "wifi settings",
        "wi-fi settings",
    ]:
        return open_wifi_settings()

    if command in [
        "open bluetooth settings",
        "bluetooth settings",
    ]:
        return open_bluetooth_settings()

    if command in [
        "open network settings",
        "network settings",
    ]:
        return open_network_settings()

    if command in [
        "open sound settings",
        "sound settings",
        "audio settings",
    ]:
        return open_sound_settings()

    if command in [
        "open display settings",
        "display settings",
        "screen settings",
    ]:
        return open_display_settings()

    # =====================================================
    # LOCK
    # =====================================================

    if command in [
        "lock",
        "lock computer",
        "lock pc",
        "computer lock karo",
    ]:
        return lock_computer()

    return None