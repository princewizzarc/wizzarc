import os
import re
import shutil
import subprocess
from pathlib import Path

import psutil
from send2trash import send2trash

from actions.file_system_manager import (
    find_item_all_drives,
    get_drive_items_text,
    get_drive_list_text,
    open_item_in_drive,
    search_drive_text,
    create_folder_in_drive,
    move_item_to_drive,
    copy_item_to_drive,
)

from actions.window_manager import (
    minimize_window,
    maximize_window,
    restore_window,
    switch_to_window,
    close_window,
    minimize_current_window,
    maximize_current_window,
    restore_current_window,
    close_current_window,
    list_open_windows,
)


from actions.input_manager import (
    press_key,
    press_hotkey,
    type_text,
    left_click,
    double_click,
    right_click,
    scroll_up,
    scroll_down,
    move_mouse,
    click_at,
    get_mouse_position,
)


from actions.clipboard_manager import (
    copy_text_to_clipboard,
    get_clipboard_text,
    clear_clipboard,
    paste_clipboard,
    save_clipboard_to_file,
    copy_selected_text,
)


from actions.browser_manager import (
    open_website,
    search_google,
    search_youtube,
    new_tab,
    close_tab,
    next_tab,
    previous_tab,
    refresh_page,
    go_back,
    go_forward,
    focus_address_bar,
)


from actions.media_manager import (
    play_pause_media,
    play_media,
    pause_media,
    next_track,
    previous_track,
    stop_media,
)


from actions.screenshot_manager import (
    take_screenshot,
    open_screenshot_folder,
    get_screen_size,
    get_current_mouse_position,
)


from actions.multi_action_manager import (
    is_multi_command,
    execute_multi_command,
)


from actions.automation_manager import (
    schedule_delayed_command,
    schedule_repeating_command,
    cancel_automation,
    list_automations,
    clear_finished_automations,
    save_automation,
    remove_saved_automation,
    list_saved_automations,
    parse_duration,
    get_delay_until_time,
)

from actions.screen_text_reader import (
    read_screen_text,
    read_region_text,
    find_text_on_screen,
    get_first_text_position,
    get_text_position,
)

from actions.screen_understanding import (
    get_screen_summary,
    show_visible_elements,
    show_clickable_elements,
    show_snapshot_clickable_elements,
    refresh_screen_snapshot,
    clear_screen_snapshot,
    get_screen_snapshot_status,
    get_screen_change_status,
    get_screen_context_summary,
    get_nearby_text_context,
    get_clickable_element_position,
    is_text_visible,
    where_is_text,
)


# =========================================================
# APP ALIASES
# =========================================================

APP_ALIASES = {
    "vs code": "visual studio code",
    "vscode": "visual studio code",
    "calc": "calculator",
    "file explorer": "explorer",
    "google chrome": "chrome",
    "microsoft edge": "edge",
}


# =========================================================
# APP PROCESS NAMES
# =========================================================

APP_PROCESSES = {
    "chrome": [
        "chrome.exe",
    ],

    "edge": [
        "msedge.exe",
    ],

    "discord": [
        "discord.exe",
    ],

    "whatsapp": [
        "whatsapp.exe",
    ],

    "visual studio code": [
        "code.exe",
    ],

    "notepad": [
        "notepad.exe",
    ],

    "paint": [
        "mspaint.exe",
    ],

    "calculator": [
        "calculatorapp.exe",
        "calculator.exe",
    ],

    "powershell": [
        "powershell.exe",
        "pwsh.exe",
    ],

    "explorer": [
        "explorer.exe",
    ],
}


# =========================================================
# KNOWN WINDOWS FOLDERS
# =========================================================

def get_known_folders():

    home = Path.home()

    return {
        "desktop":
            home / "Desktop",

        "documents":
            home / "Documents",

        "downloads":
            home / "Downloads",

        "pictures":
            home / "Pictures",

        "music":
            home / "Music",

        "videos":
            home / "Videos",
    }


# =========================================================
# FAST SEARCH LOCATIONS
# =========================================================

def get_search_locations():

    folders = get_known_folders()

    locations = [
        folders["desktop"],
        folders["documents"],
        folders["downloads"],
        folders["pictures"],
        folders["videos"],
        folders["music"],
    ]

    return [
        location
        for location in locations
        if location.exists()
    ]


# =========================================================
# NORMALIZE FILE / FOLDER NAME
# =========================================================

def normalize_item_name(name):

    name = (
        str(name)
        .lower()
        .strip()
    )

    return re.sub(
        r"[^a-z0-9]+",
        "",
        name
    )


# =========================================================
# FIND ITEM
# FAST LOCATIONS FIRST
# FULL DRIVE SEARCH SECOND
# =========================================================

def find_item(
    name,
    only_folder=False,
    only_file=False
):

    original_name = (
        str(name)
        .strip()
    )

    if not original_name:
        return None

    search_name = (
        original_name
        .lower()
    )

    normalized_search = (
        normalize_item_name(
            original_name
        )
    )

    partial_match = None

    # =====================================================
    # FAST SEARCH
    # =====================================================

    for location in get_search_locations():

        try:

            for item in location.rglob("*"):

                try:

                    if (
                        only_folder
                        and not item.is_dir()
                    ):
                        continue

                    if (
                        only_file
                        and not item.is_file()
                    ):
                        continue

                except OSError:
                    continue

                item_name = (
                    item.name
                    .lower()
                )

                # Exact match

                if item_name == search_name:

                    return item

                # Voice-friendly match

                normalized_item = (
                    normalize_item_name(
                        item.name
                    )
                )

                if (
                    normalized_search
                    and
                    normalized_item
                    == normalized_search
                ):

                    return item

                # Partial fallback

                if (
                    partial_match is None
                    and
                    search_name in item_name
                ):

                    partial_match = item

        except (
            PermissionError,
            OSError,
        ):

            continue

    # =====================================================
    # COMMON LOCATION PARTIAL
    # =====================================================

    if partial_match is not None:

        return partial_match

    # =====================================================
    # FULL DRIVE FALLBACK
    # =====================================================

    return find_item_all_drives(
        original_name,
        only_folder=only_folder,
        only_file=only_file
    )


# =========================================================
# FIND FOLDER
# =========================================================

def find_folder(name):

    return find_item(
        name,
        only_folder=True
    )


# =========================================================
# FIND FILE
# =========================================================

def find_file(name):

    return find_item(
        name,
        only_file=True
    )


# =========================================================
# LIST KNOWN LOCATION ITEMS
# =========================================================

def list_items(
    location,
    folders_only=False,
    files_only=False
):

    location = (
        str(location)
        .lower()
        .strip()
    )

    folders = get_known_folders()

    if location not in folders:

        return (
            None,
            f"Unknown location: {location}"
        )

    target = (
        folders[
            location
        ]
    )

    if not target.exists():

        return (
            None,
            (
                f"{location.title()} "
                "folder was not found."
            )
        )

    items = []

    try:

        for item in target.iterdir():

            try:

                if (
                    folders_only
                    and not item.is_dir()
                ):
                    continue

                if (
                    files_only
                    and not item.is_file()
                ):
                    continue

                items.append(
                    item
                )

            except OSError:

                continue

    except Exception as error:

        return (
            None,
            (
                f"Couldn't read "
                f"{location.title()}: "
                f"{error}"
            )
        )

    items.sort(
        key=lambda item: (
            not item.is_dir(),
            item.name.lower()
        )
    )

    return (
        items,
        None
    )


# =========================================================
# LIST KNOWN LOCATION TEXT
# =========================================================

def get_item_list_text(
    location,
    folders_only=False,
    files_only=False
):

    items, error = list_items(
        location,
        folders_only=folders_only,
        files_only=files_only
    )

    if error:
        return error

    if not items:

        if folders_only:

            return (
                f"No folders found in "
                f"{location.title()}."
            )

        if files_only:

            return (
                f"No files found in "
                f"{location.title()}."
            )

        return (
            f"No items found in "
            f"{location.title()}."
        )

    lines = []

    for item in items:

        try:

            if item.is_dir():

                lines.append(
                    f"[Folder] {item.name}"
                )

            else:

                lines.append(
                    f"[File] {item.name}"
                )

        except OSError:

            continue

    return (
        f"{location.title()} — "
        f"{len(lines)} item(s)\n\n"
        + "\n".join(lines)
    )


# =========================================================
# OPEN KNOWN FOLDER
# =========================================================

def open_known_folder(
    folder_name
):

    folder_name = (
        str(folder_name)
        .strip()
        .lower()
    )

    folders = get_known_folders()

    if folder_name not in folders:

        return None

    target = (
        folders[
            folder_name
        ]
    )

    if not target.exists():

        return (
            f"{folder_name.title()} "
            "folder was not found."
        )

    try:

        os.startfile(
            str(target)
        )

        return (
            f"{folder_name.title()} "
            "folder opened."
        )

    except Exception as error:

        return (
            f"Couldn't open "
            f"{folder_name}: {error}"
        )


# =========================================================
# OPEN FILE / FOLDER ANYWHERE
# =========================================================

def open_file_or_folder(
    name,
    only_folder=False,
    only_file=False
):

    found = find_item(
        name,
        only_folder=only_folder,
        only_file=only_file
    )

    if not found:

        return (
            f"I couldn't find "
            f"'{name}' on this computer."
        )

    try:

        os.startfile(
            str(found)
        )

        return (
            f"{found.name} opened."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to open '{found.name}'."
        )

    except Exception as error:

        return (
            f"Couldn't open "
            f"'{found.name}': {error}"
        )


# =========================================================
# CREATE FOLDER
# =========================================================

def create_folder(
    folder_name,
    location="documents"
):

    folders = get_known_folders()

    location = (
        str(location)
        .lower()
        .strip()
    )

    if location not in folders:

        return (
            f"Unknown location: "
            f"{location}"
        )

    base_location = (
        folders[
            location
        ]
    )

    if not base_location.exists():

        return (
            f"{location.title()} "
            "folder was not found."
        )

    folder_name = (
        str(folder_name)
        .strip()
    )

    if not folder_name:

        return (
            "Folder name is empty."
        )

    target = (
        base_location
        / folder_name
    )

    if target.exists():

        return (
            f"'{folder_name}' "
            "already exists."
        )

    try:

        target.mkdir()

        return (
            f"Folder '{folder_name}' "
            f"created in "
            f"{location.title()}."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to create '{folder_name}' "
            f"in {location.title()}."
        )

    except Exception as error:

        return (
            f"Couldn't create folder: "
            f"{error}"
        )


# =========================================================
# RENAME ITEM
# =========================================================

def rename_item(
    old_name,
    new_name
):

    item = find_item(
        old_name
    )

    if not item:

        return (
            f"I couldn't find "
            f"'{old_name}'."
        )

    target = (
        item.parent
        / str(new_name).strip()
    )

    if (
        item.is_file()
        and not target.suffix
    ):

        target = target.with_suffix(
            item.suffix
        )

    if target.exists():

        return (
            f"'{target.name}' "
            "already exists."
        )

    old_item_name = (
        item.name
    )

    try:

        item.rename(
            target
        )

        return (
            f"Renamed "
            f"'{old_item_name}' "
            f"to '{target.name}'."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to rename '{old_item_name}'."
        )

    except Exception as error:

        return (
            f"Couldn't rename item: "
            f"{error}"
        )


# =========================================================
# MOVE TO KNOWN LOCATION
# =========================================================

def move_item(
    item_name,
    destination
):

    item = find_item(
        item_name
    )

    if not item:

        return (
            f"I couldn't find "
            f"'{item_name}'."
        )

    folders = get_known_folders()

    destination = (
        str(destination)
        .lower()
        .strip()
    )

    if destination not in folders:

        return (
            f"Unknown destination: "
            f"{destination}"
        )

    destination_path = (
        folders[
            destination
        ]
    )

    if not destination_path.exists():

        return (
            f"{destination.title()} "
            "folder was not found."
        )

    target = (
        destination_path
        / item.name
    )

    if target.exists():

        return (
            f"'{item.name}' already "
            f"exists in "
            f"{destination.title()}."
        )

    try:

        shutil.move(
            str(item),
            str(target)
        )

        return (
            f"Moved '{item.name}' "
            f"to {destination.title()}."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to move '{item.name}'."
        )

    except Exception as error:

        return (
            f"Couldn't move item: "
            f"{error}"
        )


# =========================================================
# COPY TO KNOWN LOCATION
# =========================================================

def copy_item(
    item_name,
    destination
):

    item = find_item(
        item_name
    )

    if not item:

        return (
            f"I couldn't find "
            f"'{item_name}'."
        )

    folders = get_known_folders()

    destination = (
        str(destination)
        .lower()
        .strip()
    )

    if destination not in folders:

        return (
            f"Unknown destination: "
            f"{destination}"
        )

    destination_path = (
        folders[
            destination
        ]
    )

    if not destination_path.exists():

        return (
            f"{destination.title()} "
            "folder was not found."
        )

    target = (
        destination_path
        / item.name
    )

    if target.exists():

        return (
            f"'{item.name}' already "
            f"exists in "
            f"{destination.title()}."
        )

    try:

        if item.is_dir():

            shutil.copytree(
                item,
                target
            )

        else:

            shutil.copy2(
                item,
                target
            )

        return (
            f"Copied '{item.name}' "
            f"to {destination.title()}."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to copy '{item.name}'."
        )

    except Exception as error:

        return (
            f"Couldn't copy item: "
            f"{error}"
        )


# =========================================================
# PREPARE DELETE
# =========================================================

def prepare_delete(
    command
):

    command = (
        str(command)
        .strip()
        .lower()
    )

    if command.startswith(
        "delete folder "
    ):

        name = command[
            len("delete folder "):
        ].strip()

        item = find_folder(
            name
        )

        if not item:

            return (
                None,
                (
                    "I couldn't find "
                    f"folder '{name}'."
                )
            )

        return (
            item,
            None
        )

    if command.startswith(
        "delete file "
    ):

        name = command[
            len("delete file "):
        ].strip()

        item = find_file(
            name
        )

        if not item:

            return (
                None,
                (
                    "I couldn't find "
                    f"file '{name}'."
                )
            )

        return (
            item,
            None
        )

    return (
        None,
        None
    )


# =========================================================
# DELETE ITEM
# =========================================================

def delete_item(
    path
):

    try:

        send2trash(
            str(path)
        )

        return (
            f"'{Path(path).name}' "
            "moved to Recycle Bin."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to delete '{Path(path).name}'."
        )

    except Exception as error:

        return (
            f"Couldn't delete item: "
            f"{error}"
        )


# =========================================================
# FIND START MENU APP
# =========================================================

def find_start_menu_app(
    app_name
):

    locations = [

        Path(
            os.environ.get(
                "APPDATA",
                ""
            )
        )
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs",

        Path(
            os.environ.get(
                "PROGRAMDATA",
                ""
            )
        )
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs",
    ]

    app_name = (
        str(app_name)
        .lower()
        .strip()
    )

    app_name = (
        APP_ALIASES.get(
            app_name,
            app_name
        )
    )

    partial = None

    for location in locations:

        if not location.exists():
            continue

        try:

            for shortcut in (
                location.rglob(
                    "*.lnk"
                )
            ):

                shortcut_name = (
                    shortcut
                    .stem
                    .lower()
                )

                if (
                    shortcut_name
                    == app_name
                ):

                    return shortcut

                if (
                    app_name
                    in shortcut_name
                    and partial is None
                ):

                    partial = shortcut

        except (
            PermissionError,
            OSError,
        ):

            continue

    return partial


# =========================================================
# OPEN APP
# =========================================================

def open_app(
    app_name
):

    app_name = (
        str(app_name)
        .lower()
        .strip()
    )

    normalized = (
        APP_ALIASES.get(
            app_name,
            app_name
        )
    )

    built_in_apps = {

        "notepad":
            "notepad.exe",

        "calculator":
            "calc.exe",

        "paint":
            "mspaint.exe",

        "cmd":
            "cmd.exe",

        "command prompt":
            "cmd.exe",

        "powershell":
            "powershell.exe",

        "explorer":
            "explorer.exe",
    }

    # =====================================================
    # SETTINGS
    # =====================================================

    if normalized == "settings":

        try:

            os.startfile(
                "ms-settings:"
            )

            return (
                "Settings opened."
            )

        except Exception as error:

            return (
                f"Couldn't open Settings: "
                f"{error}"
            )

    # =====================================================
    # BUILT-IN APP
    # =====================================================

    if normalized in built_in_apps:

        try:

            subprocess.Popen(
                [
                    built_in_apps[
                        normalized
                    ]
                ]
            )

            return (
                f"{app_name.title()} "
                "opened."
            )

        except Exception as error:

            return (
                f"Couldn't open "
                f"{app_name}: {error}"
            )

    # =====================================================
    # PATH COMMAND
    # =====================================================

    executable = shutil.which(
        normalized
    )

    if executable:

        try:

            subprocess.Popen(
                [executable]
            )

            return (
                f"{app_name.title()} "
                "opened."
            )

        except Exception:
            pass

    # =====================================================
    # START MENU
    # =====================================================

    shortcut = find_start_menu_app(
        normalized
    )

    if shortcut:

        try:

            os.startfile(
                str(shortcut)
            )

            return (
                f"{app_name.title()} "
                "opened."
            )

        except Exception as error:

            return (
                f"Couldn't open "
                f"{app_name}: {error}"
            )

    # =====================================================
    # COMMON PATHS
    # =====================================================

    common_paths = {

        "chrome": [

            r"C:\Program Files\Google\Chrome\Application\chrome.exe",

            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",

            os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
            ),
        ],

        "edge": [

            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",

            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ],

        "visual studio code": [

            os.path.expandvars(
                r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"
            ),
        ],
    }

    if normalized in common_paths:

        for path in common_paths[
            normalized
        ]:

            if os.path.exists(
                path
            ):

                try:

                    subprocess.Popen(
                        [path]
                    )

                    return (
                        f"{app_name.title()} "
                        "opened."
                    )

                except Exception as error:

                    return (
                        f"Couldn't open "
                        f"{app_name}: {error}"
                    )

    return (
        f"I couldn't find an app "
        f"called '{app_name}'."
    )


# =========================================================
# GET PROCESS NAMES
# =========================================================

def get_process_names(
    app_name
):

    app_name = (
        str(app_name)
        .lower()
        .strip()
    )

    normalized = (
        APP_ALIASES.get(
            app_name,
            app_name
        )
    )

    if normalized in APP_PROCESSES:

        return (
            APP_PROCESSES[
                normalized
            ]
        )

    if app_name in APP_PROCESSES:

        return (
            APP_PROCESSES[
                app_name
            ]
        )

    return [
        f"{normalized}.exe"
    ]


# =========================================================
# CHECK APP RUNNING
# =========================================================

def is_app_running(
    app_name
):

    process_names = {
        name.lower()
        for name in (
            get_process_names(
                app_name
            )
        )
    }

    for process in (
        psutil.process_iter(
            ["name"]
        )
    ):

        try:

            process_name = (
                process.info.get(
                    "name"
                )
                or ""
            ).lower()

            if (
                process_name
                in process_names
            ):

                return True

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):

            continue

    return False


# =========================================================
# CLOSE APP
# =========================================================

def close_app(
    app_name
):

    app_name = (
        str(app_name)
        .lower()
        .strip()
    )

    process_names = {
        name.lower()
        for name in (
            get_process_names(
                app_name
            )
        )
    }

    matched_processes = []

    for process in (
        psutil.process_iter(
            ["name"]
        )
    ):

        try:

            process_name = (
                process.info.get(
                    "name"
                )
                or ""
            ).lower()

            if (
                process_name
                in process_names
            ):

                matched_processes.append(
                    process
                )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):

            continue

    if not matched_processes:

        return (
            f"{app_name.title()} "
            "is not running."
        )

    terminated = 0

    for process in matched_processes:

        try:

            process.terminate()

            terminated += 1

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):

            continue

    try:

        gone, alive = (
            psutil.wait_procs(
                matched_processes,
                timeout=3
            )
        )

    except Exception:

        alive = []

    for process in alive:

        try:

            process.kill()

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):

            continue

    if terminated == 0:

        return (
            f"I found "
            f"{app_name.title()}, "
            "but couldn't close it."
        )

    return (
        f"{app_name.title()} "
        "closed."
    )


# =========================================================
# EXECUTE COMMAND
# =========================================================

def execute_command(
    command
):

    command = (
        str(command)
        .strip()
        .lower()
    )

    if not command:

        return (
            "Please enter a command."
        )




    # =====================================================
    # PHASE 6 - SCREEN TEXT / OCR
    # =====================================================

    if command in {
        "read screen",
        "read text on screen",
    }:
        return read_screen_text()

    match = re.fullmatch(
        r"read region (-?\d+) (-?\d+) (\d+) (\d+)",
        command
    )

    if match:
        return read_region_text(
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4)
        )

    match = re.fullmatch(
        r"find text (.+?) on screen",
        command
    )

    if match:
        search_text = match.group(1).strip()

        if not search_text:
            return "Please tell me what text to find."

        return find_text_on_screen(search_text)






    # =====================================================
    # PHASE 6 - SCREEN UNDERSTANDING
    # =====================================================

    if command in {
        "what can you see",
        "what is on my screen",
    }:

        return get_screen_summary()

    if command == "show visible elements":

        return show_visible_elements()


    if command == "show clickable elements":

        return show_clickable_elements()


    # =====================================================
    # PHASE 6 - SCREEN SNAPSHOT CACHE
    # =====================================================

    if command == "refresh screen snapshot":

        return refresh_screen_snapshot()

    if command == "clear screen snapshot":

        return clear_screen_snapshot()


    if command == "screen snapshot status":

        return get_screen_snapshot_status()

    if command == "screen change status":

        return get_screen_change_status()


    # =====================================================
    # PHASE 6 - SCREEN CONTEXT / GROUPING
    # =====================================================

    if command == "show screen context":

        return get_screen_context_summary()

    match = re.fullmatch(
        r"context around (.+)",
        command
    )

    if match:

        search_text = (
            match.group(1)
            .strip()
        )

        if not search_text:

            return (
                "Please tell me which text "
                "you want context for."
            )

        return get_nearby_text_context(
            search_text
        )

    if command == "show cached clickable elements":

        return show_snapshot_clickable_elements()


    # =====================================================
    # PHASE 6 - NUMBERED CLICKABLE ELEMENT ACTIONS
    # Examples:
    # click element 5
    # move to element 3
    # double click element 2
    # right click element 4
    # =====================================================

    match = re.fullmatch(
        r"click element (\d+)",
        command
    )

    if match:

        number = (
            match.group(1)
        )

        x, y, text, error = (
            get_clickable_element_position(
                number
            )
        )

        if error:

            return error

        result = click_at(
            x,
            y
        )

        return (
            f"Clicked element {number} "
            f"'{text}' at {x}, {y}. "
            f"{result}"
        )

    match = re.fullmatch(
        r"move to element (\d+)",
        command
    )

    if match:

        number = (
            match.group(1)
        )

        x, y, text, error = (
            get_clickable_element_position(
                number
            )
        )

        if error:

            return error

        result = move_mouse(
            x,
            y
        )

        return (
            f"Moved to element {number} "
            f"'{text}' at {x}, {y}. "
            f"{result}"
        )

    match = re.fullmatch(
        r"double click element (\d+)",
        command
    )

    if match:

        number = (
            match.group(1)
        )

        x, y, text, error = (
            get_clickable_element_position(
                number
            )
        )

        if error:

            return error

        move_mouse(
            x,
            y
        )

        result = double_click()

        return (
            f"Double clicked element {number} "
            f"'{text}' at {x}, {y}. "
            f"{result}"
        )

    match = re.fullmatch(
        r"right click element (\d+)",
        command
    )

    if match:

        number = (
            match.group(1)
        )

        x, y, text, error = (
            get_clickable_element_position(
                number
            )
        )

        if error:

            return error

        move_mouse(
            x,
            y
        )

        result = right_click()

        return (
            f"Right clicked element {number} "
            f"'{text}' at {x}, {y}. "
            f"{result}"
        )

    match = re.fullmatch(
        r"is (.+?) visible",
        command
    )

    if match:

        search_text = (
            match.group(1)
            .strip()
        )

        if not search_text:

            return (
                "Please tell me what "
                "to look for."
            )

        return is_text_visible(
            search_text
        )

    match = re.fullmatch(
        r"where is (.+)",
        command
    )

    if match:

        search_text = (
            match.group(1)
            .strip()
        )

        if not search_text:

            return (
                "Please tell me what "
                "to locate."
            )

        return where_is_text(
            search_text
        )

    # =====================================================
    # PHASE 6 - FIND + ACTION COMBINATIONS
    # Examples:
    # find and click text settings
    # find and double click text downloads
    # find and right click text file
    # =====================================================

    if command.startswith(
        "find and click text "
    ):

        search_text = command[
            len("find and click text "):
        ].strip()

        if not search_text:

            return (
                "Please tell me what text "
                "to find and click."
            )

        x, y, error = (
            get_first_text_position(
                search_text
            )
        )

        if error:

            return error

        click_result = click_at(
            x,
            y
        )

        return (
            f"Found and clicked '{search_text}' "
            f"at {x}, {y}. "
            f"{click_result}"
        )

    if command.startswith(
        "find and double click text "
    ):

        search_text = command[
            len("find and double click text "):
        ].strip()

        if not search_text:

            return (
                "Please tell me what text "
                "to find and double click."
            )

        x, y, error = (
            get_first_text_position(
                search_text
            )
        )

        if error:

            return error

        move_result = move_mouse(
            x,
            y
        )

        click_result = double_click()

        return (
            f"Found and double clicked "
            f"'{search_text}' at {x}, {y}. "
            f"{move_result} {click_result}"
        )

    if command.startswith(
        "find and right click text "
    ):

        search_text = command[
            len("find and right click text "):
        ].strip()

        if not search_text:

            return (
                "Please tell me what text "
                "to find and right click."
            )

        x, y, error = (
            get_first_text_position(
                search_text
            )
        )

        if error:

            return error

        move_result = move_mouse(
            x,
            y
        )

        click_result = right_click()

        return (
            f"Found and right clicked "
            f"'{search_text}' at {x}, {y}. "
            f"{move_result} {click_result}"
        )

    # =====================================================
    # PHASE 6 - TEXT TARGET MOUSE ACTIONS
    # Examples:
    # move to text terminal
    # double click text file
    # right click text settings
    # =====================================================

    if command.startswith(
        "move to text "
    ):

        search_text = command[
            len("move to text "):
        ].strip()

        if not search_text:

            return (
                "Please tell me what text "
                "to move to."
            )

        x, y, error = (
            get_first_text_position(
                search_text
            )
        )

        if error:

            return error

        return move_mouse(
            x,
            y
        )

    if command.startswith(
        "double click text "
    ):

        search_text = command[
            len("double click text "):
        ].strip()

        if not search_text:

            return (
                "Please tell me what text "
                "to double click."
            )

        x, y, error = (
            get_first_text_position(
                search_text
            )
        )

        if error:

            return error

        move_result = move_mouse(
            x,
            y
        )

        click_result = double_click()

        return (
            f"Double clicked '{search_text}' "
            f"at {x}, {y}. "
            f"{move_result} {click_result}"
        )

    if command.startswith(
        "right click text "
    ):

        search_text = command[
            len("right click text "):
        ].strip()

        if not search_text:

            return (
                "Please tell me what text "
                "to right click."
            )

        x, y, error = (
            get_first_text_position(
                search_text
            )
        )

        if error:

            return error

        move_result = move_mouse(
            x,
            y
        )

        click_result = right_click()

        return (
            f"Right clicked '{search_text}' "
            f"at {x}, {y}. "
            f"{move_result} {click_result}"
        )

    # =====================================================
    # PHASE 6 - CLICK SELECTED TEXT MATCH
    # Examples:
    # click first text terminal
    # click second text terminal
    # click last text terminal
    # click 3 text terminal
    # =====================================================

    match = re.fullmatch(
        (
            r"click "
            r"(first|second|third|last|\d+) "
            r"text (.+)"
        ),
        command
    )

    if match:

        selector = (
            match.group(1)
            .strip()
        )

        search_text = (
            match.group(2)
            .strip()
        )

        if not search_text:

            return (
                "Please tell me what text "
                "to click."
            )

        x, y, error = (
            get_text_position(
                search_text,
                selector
            )
        )

        if error:

            return error

        click_result = click_at(
            x,
            y
        )

        return (
            f"Clicked {selector} "
            f"'{search_text}' match "
            f"at {x}, {y}. "
            f"{click_result}"
        )

    # =====================================================
    # PHASE 6 - CLICK TEXT ON SCREEN
    # Example:
    # click text terminal
    # =====================================================

    if command.startswith(
        "click text "
    ):

        search_text = command[
            len("click text "):
        ].strip()

        if not search_text:

            return (
                "Please tell me what text "
                "to click."
            )

        x, y, error = (
            get_first_text_position(
                search_text
            )
        )

        if error:

            return error

        click_result = click_at(
            x,
            y
        )

        return (
            f"Clicked '{search_text}' "
            f"at {x}, {y}. "
            f"{click_result}"
        )

    # =====================================================
    # PHASE 5 - AUTOMATION
    # =====================================================


    # =====================================================
    # PHASE 5 - AUTOMATION PERSISTENCE
    # =====================================================

    if command == "show saved automations":

        return list_saved_automations()

    if command.startswith(
        "save automation "
    ):

        automation_id = command[
            len("save automation "):
        ].strip()

        return save_automation(
            automation_id
        )

    if command.startswith(
        "remove saved automation "
    ):

        automation_id = command[
            len("remove saved automation "):
        ].strip()

        return remove_saved_automation(
            automation_id
        )

    if command == "show automations":
        return list_automations()

    if command == "clear finished automations":
        return clear_finished_automations()

    if command.startswith(
        "cancel automation "
    ):
        automation_id = command[
            len("cancel automation "):
        ].strip()

        if not automation_id:
            return "Please tell me which automation to cancel."

        return cancel_automation(
            automation_id
        )




    # =====================================================
    # REPEATING AUTOMATION WITH STOP-AFTER DURATION
    # Example:
    # take screenshot every 10 minutes for 1 hour
    # =====================================================

    match = re.fullmatch(
        (
            r"(.+?) every "
            r"(\d+(?:\.\d+)?) "
            r"(seconds?|minutes?|hours?) "
            r"for "
            r"(\d+(?:\.\d+)?) "
            r"(seconds?|minutes?|hours?)"
        ),
        command
    )

    if match:

        repeat_command = (
            match.group(1)
            .strip()
        )

        interval_value = (
            match.group(2)
            .strip()
        )

        interval_unit = (
            match.group(3)
            .strip()
        )

        stop_value = (
            match.group(4)
            .strip()
        )

        stop_unit = (
            match.group(5)
            .strip()
        )

        interval_seconds = parse_duration(
            interval_value,
            interval_unit
        )

        stop_after_seconds = parse_duration(
            stop_value,
            stop_unit
        )

        if interval_seconds is None:

            return (
                "I couldn't understand "
                "that repeat interval."
            )

        if stop_after_seconds is None:

            return (
                "I couldn't understand "
                "the stop-after duration."
            )

        return schedule_repeating_command(
            repeat_command,
            interval_seconds,
            execute_command,
            stop_after_seconds=stop_after_seconds
        )

    # =====================================================
    # REPEATING AUTOMATION WITH COUNT
    # Example:
    # take screenshot every 5 minutes 3 times
    # =====================================================

    match = re.fullmatch(
        (
            r"(.+?) every "
            r"(\d+(?:\.\d+)?) "
            r"(seconds?|minutes?|hours?) "
            r"(\d+) times?"
        ),
        command
    )

    if match:

        repeat_command = (
            match.group(1)
            .strip()
        )

        value = (
            match.group(2)
            .strip()
        )

        unit = (
            match.group(3)
            .strip()
        )

        max_runs = (
            match.group(4)
            .strip()
        )

        interval_seconds = parse_duration(
            value,
            unit
        )

        if interval_seconds is None:

            return (
                "I couldn't understand "
                "that repeat interval."
            )

        return schedule_repeating_command(
            repeat_command,
            interval_seconds,
            execute_command,
            max_runs=max_runs
        )

    # =====================================================
    # REPEATING AUTOMATION
    # Example:
    # take screenshot every 10 minutes
    # =====================================================

    match = re.fullmatch(
        (
            r"(.+?) every "
            r"(\d+(?:\.\d+)?) "
            r"(seconds?|minutes?|hours?)"
        ),
        command
    )

    if match:

        repeat_command = (
            match.group(1)
            .strip()
        )

        value = (
            match.group(2)
            .strip()
        )

        unit = (
            match.group(3)
            .strip()
        )

        interval_seconds = parse_duration(
            value,
            unit
        )

        if interval_seconds is None:

            return (
                "I couldn't understand "
                "that repeat interval."
            )

        return schedule_repeating_command(
            repeat_command,
            interval_seconds,
            execute_command
        )

    match = re.fullmatch(
        (
            r"(.+?) after "
            r"(\d+(?:\.\d+)?) "
            r"(seconds?|minutes?|hours?)"
        ),
        command
    )

    if match:

        delayed_command = (
            match.group(1)
            .strip()
        )

        value = (
            match.group(2)
            .strip()
        )

        unit = (
            match.group(3)
            .strip()
        )

        delay_seconds = parse_duration(
            value,
            unit
        )

        if delay_seconds is None:

            return (
                "I couldn't understand "
                "that duration."
            )

        return schedule_delayed_command(
            delayed_command,
            delay_seconds,
            execute_command
        )


    # =====================================================
    # EXACT TIME AUTOMATION
    # Example:
    # open chrome at 6:30 pm
    # =====================================================

    match = re.fullmatch(
        (
            r"(.+?) at "
            r"(\d{1,2}(?::\d{2})?"
            r"(?:\s*(?:am|pm))?)"
        ),
        command
    )

    if match:

        scheduled_command = (
            match.group(1)
            .strip()
        )

        time_text = (
            match.group(2)
            .strip()
        )

        delay_seconds = (
            get_delay_until_time(
                time_text
            )
        )

        if delay_seconds is None:

            return (
                "I couldn't understand "
                "that time."
            )

        return schedule_delayed_command(
            scheduled_command,
            delay_seconds,
            execute_command
        )

    # =====================================================
    # PHASE 4 - MULTI STEP COMMANDS
    # =====================================================

    if is_multi_command(command):
        return execute_multi_command(
            command,
            execute_command
        )

    # =====================================================
    # PHASE 4 - CURRENT WINDOW CONTROL
    # =====================================================

    if command == "minimize current window":

        return minimize_current_window()

    if command == "maximize current window":

        return maximize_current_window()

    if command == "restore current window":

        return restore_current_window()

    if command == "close current window":

        return close_current_window()

    # =====================================================
    # SHOW OPEN WINDOWS
    # =====================================================

    if command == "show open windows":

        return list_open_windows()

    # =====================================================
    # CLOSE SPECIFIC WINDOW
    # =====================================================

    if command.startswith(
        "close window "
    ):

        name = command[
            len("close window "):
        ].strip()

        if not name:

            return (
                "Please tell me which "
                "window to close."
            )

        return close_window(
            name
        )

    # =====================================================
    # SWITCH WINDOW
    # =====================================================

    if command.startswith(
        "switch to "
    ):

        name = command[
            len("switch to "):
        ].strip()

        if not name:

            return (
                "Please tell me which "
                "window to switch to."
            )

        return switch_to_window(
            name
        )

    # =====================================================
    # MINIMIZE SPECIFIC WINDOW
    # =====================================================

    if command.startswith(
        "minimize "
    ):

        name = command[
            len("minimize "):
        ].strip()

        if not name:

            return (
                "Please tell me which "
                "window to minimize."
            )

        return minimize_window(
            name
        )

    # =====================================================
    # MAXIMIZE SPECIFIC WINDOW
    # =====================================================

    if command.startswith(
        "maximize "
    ):

        name = command[
            len("maximize "):
        ].strip()

        if not name:

            return (
                "Please tell me which "
                "window to maximize."
            )

        return maximize_window(
            name
        )

    # =====================================================
    # RESTORE SPECIFIC WINDOW
    # =====================================================

    if command.startswith(
        "restore "
    ):

        name = command[
            len("restore "):
        ].strip()

        if not name:

            return (
                "Please tell me which "
                "window to restore."
            )

        return restore_window(
            name
        )

    # =====================================================
    # PHASE 4 - KEYBOARD / MOUSE CONTROL
    # =====================================================

    if command == "click":
        return left_click()

    if command == "double click":
        return double_click()

    if command == "right click":
        return right_click()

    if command == "mouse position":
        return get_mouse_position()

    if command.startswith(
        "type "
    ):
        text = command[
            len("type "):
        ]

        if not text:
            return "Please tell me what to type."

        return type_text(text)

    match = re.fullmatch(
        r"scroll up(?: (\d+))?",
        command
    )

    if match:
        amount = match.group(1) or 5
        return scroll_up(amount)

    match = re.fullmatch(
        r"scroll down(?: (\d+))?",
        command
    )

    if match:
        amount = match.group(1) or 5
        return scroll_down(amount)

    match = re.fullmatch(
        r"move mouse to (\d+) (\d+)",
        command
    )

    if match:
        return move_mouse(
            match.group(1),
            match.group(2)
        )

    match = re.fullmatch(
        r"click at (\d+) (\d+)",
        command
    )

    if match:
        return click_at(
            match.group(1),
            match.group(2)
        )

    if command.startswith(
        "press "
    ):
        keys = command[
            len("press "):
        ].split()

        if not keys:
            return (
                "Please tell me which key "
                "or shortcut to press."
            )

        if len(keys) == 1:
            return press_key(
                keys[0]
            )

        return press_hotkey(
            *keys
        )


    # =====================================================
    # PHASE 4 - CLIPBOARD CONTROL
    # =====================================================

    if command == "show clipboard":
        return get_clipboard_text()

    if command == "clear clipboard":
        return clear_clipboard()

    if command == "paste clipboard":
        return paste_clipboard()

    if command == "copy selected text":
        return copy_selected_text()

    if command == "save clipboard to file":
        return save_clipboard_to_file()

    if command.startswith(
        "save clipboard to "
    ):
        filename = command[
            len("save clipboard to "):
        ].strip()

        if not filename:
            return "Please tell me the file name."

        return save_clipboard_to_file(
            filename
        )

    if command.startswith(
        "copy text "
    ):
        text = command[
            len("copy text "):
        ]

        if not text:
            return "Please tell me what text to copy."

        return copy_text_to_clipboard(
            text
        )


    # =====================================================
    # PHASE 4 - BROWSER / WEB CONTROL
    # =====================================================

    if command == "new tab":
        return new_tab()

    if command == "close tab":
        return close_tab()

    if command == "next tab":
        return next_tab()

    if command == "previous tab":
        return previous_tab()

    if command == "refresh page":
        return refresh_page()

    if command == "go back":
        return go_back()

    if command == "go forward":
        return go_forward()

    if command == "focus address bar":
        return focus_address_bar()

    if command.startswith(
        "open website "
    ):
        website = command[
            len("open website "):
        ].strip()

        if not website:
            return "Please tell me which website to open."

        return open_website(
            website
        )

    if command.startswith(
        "search google for "
    ):
        query = command[
            len("search google for "):
        ].strip()

        if not query:
            return "Please tell me what to search on Google."

        return search_google(
            query
        )

    if command.startswith(
        "search youtube for "
    ):
        query = command[
            len("search youtube for "):
        ].strip()

        if not query:
            return "Please tell me what to search on YouTube."

        return search_youtube(
            query
        )


    # =====================================================
    # PHASE 4 - MEDIA CONTROL
    # =====================================================

    if command == "play pause":
        return play_pause_media()

    if command == "play media":
        return play_media()

    if command == "pause media":
        return pause_media()

    if command == "next track":
        return next_track()

    if command == "previous track":
        return previous_track()

    if command == "stop media":
        return stop_media()


    # =====================================================
    # PHASE 4 - SCREENSHOT / SCREEN CONTROL
    # =====================================================

    if command == "take screenshot":
        return take_screenshot()

    if command == "take screenshot of screen":
        return take_screenshot()

    if command == "open screenshots folder":
        return open_screenshot_folder()

    if command == "show screen size":
        return get_screen_size()

    if command == "show mouse position":
        return get_current_mouse_position()

    if command.startswith(
        "save screenshot as "
    ):
        filename = command[
            len("save screenshot as "):
        ].strip()

        if not filename:
            return "Please tell me the screenshot name."

        return take_screenshot(
            filename
        )

    # =====================================================
    # SPECIFIC DRIVE SEARCH
    # =====================================================

    match = re.fullmatch(
        r"find (.+) in ([a-z]) drive",
        command
    )

    if match:

        name = (
            match.group(1)
            .strip()
        )

        drive = (
            match.group(2)
            .strip()
        )

        return search_drive_text(
            name,
            drive
        )

    # =====================================================
    # OPEN FOLDER IN SPECIFIC DRIVE
    # =====================================================

    match = re.fullmatch(
        r"open folder (.+) in ([a-z]) drive",
        command
    )

    if match:

        name = (
            match.group(1)
            .strip()
        )

        drive = (
            match.group(2)
            .strip()
        )

        return open_item_in_drive(
            name,
            drive,
            only_folder=True
        )

    # =====================================================
    # OPEN FILE IN SPECIFIC DRIVE
    # =====================================================

    match = re.fullmatch(
        r"open file (.+) in ([a-z]) drive",
        command
    )

    if match:

        name = (
            match.group(1)
            .strip()
        )

        drive = (
            match.group(2)
            .strip()
        )

        return open_item_in_drive(
            name,
            drive,
            only_file=True
        )

    # =====================================================
    # CREATE FOLDER IN DRIVE
    # =====================================================

    match = re.fullmatch(
        r"create folder (.+) in ([a-z]) drive",
        command
    )

    if match:

        folder_name = (
            match.group(1)
            .strip()
        )

        drive = (
            match.group(2)
            .strip()
        )

        return create_folder_in_drive(
            folder_name,
            drive
        )

    # =====================================================
    # MOVE FILE / FOLDER TO DRIVE
    # =====================================================

    match = re.fullmatch(
        r"move (file|folder) (.+) to ([a-z]) drive",
        command
    )

    if match:

        item_type = (
            match.group(1)
            .strip()
        )

        item_name = (
            match.group(2)
            .strip()
        )

        drive = (
            match.group(3)
            .strip()
        )

        item = find_item(
            item_name,
            only_file=(
                item_type == "file"
            ),
            only_folder=(
                item_type == "folder"
            )
        )

        if not item:

            return (
                f"I couldn't find "
                f"'{item_name}'."
            )

        return move_item_to_drive(
            item,
            drive
        )

    # =====================================================
    # COPY FILE / FOLDER TO DRIVE
    # =====================================================

    match = re.fullmatch(
        r"copy (file|folder) (.+) to ([a-z]) drive",
        command
    )

    if match:

        item_type = (
            match.group(1)
            .strip()
        )

        item_name = (
            match.group(2)
            .strip()
        )

        drive = (
            match.group(3)
            .strip()
        )

        item = find_item(
            item_name,
            only_file=(
                item_type == "file"
            ),
            only_folder=(
                item_type == "folder"
            )
        )

        if not item:

            return (
                f"I couldn't find "
                f"'{item_name}'."
            )

        return copy_item_to_drive(
            item,
            drive
        )

    # =====================================================
    # SHOW ALL DRIVES
    # =====================================================

    if command == "show all drives":

        return get_drive_list_text()

    # =====================================================
    # DRIVE FOLDERS
    # =====================================================

    match = re.fullmatch(
        r"show all folders in ([a-z]) drive",
        command
    )

    if match:

        drive = (
            match.group(1)
        )

        return get_drive_items_text(
            drive,
            folders_only=True
        )

    # =====================================================
    # DRIVE FILES
    # =====================================================

    match = re.fullmatch(
        r"show all files in ([a-z]) drive",
        command
    )

    if match:

        drive = (
            match.group(1)
        )

        return get_drive_items_text(
            drive,
            files_only=True
        )

    # =====================================================
    # DRIVE ALL ITEMS
    # =====================================================

    match = re.fullmatch(
        r"show (?:everything|all items) in ([a-z]) drive",
        command
    )

    if match:

        drive = (
            match.group(1)
        )

        return get_drive_items_text(
            drive
        )

    # =====================================================
    # NORMAL LOCATION LISTING
    # =====================================================

    if command.startswith(
        "show all folders in "
    ):

        location = command[
            len("show all folders in "):
        ].strip()

        return get_item_list_text(
            location,
            folders_only=True
        )

    if command.startswith(
        "show all files in "
    ):

        location = command[
            len("show all files in "):
        ].strip()

        return get_item_list_text(
            location,
            files_only=True
        )

    if command.startswith(
        "show everything in "
    ):

        location = command[
            len("show everything in "):
        ].strip()

        return get_item_list_text(
            location
        )

    if command.startswith(
        "show all items in "
    ):

        location = command[
            len("show all items in "):
        ].strip()

        return get_item_list_text(
            location
        )

    # =====================================================
    # KNOWN FOLDERS
    # =====================================================

    folder_commands = {
        "open desktop":
            "desktop",

        "open documents":
            "documents",

        "open downloads":
            "downloads",

        "open pictures":
            "pictures",

        "open music":
            "music",

        "open videos":
            "videos",
    }

    if command in folder_commands:

        return open_known_folder(
            folder_commands[
                command
            ]
        )

    # =====================================================
    # CREATE FOLDER
    # =====================================================

    if command.startswith(
        "create folder "
    ):

        text = command[
            len("create folder "):
        ].strip()

        if " in " in text:

            name, location = (
                text.rsplit(
                    " in ",
                    1
                )
            )

            return create_folder(
                name,
                location
            )

        return create_folder(
            text
        )

    # =====================================================
    # RENAME FOLDER
    # =====================================================

    if command.startswith(
        "rename folder "
    ):

        text = command[
            len("rename folder "):
        ]

        if " to " not in text:

            return (
                "Use: rename folder "
                "OLD to NEW"
            )

        old, new = (
            text.split(
                " to ",
                1
            )
        )

        return rename_item(
            old,
            new
        )

    # =====================================================
    # RENAME FILE
    # =====================================================

    if command.startswith(
        "rename file "
    ):

        text = command[
            len("rename file "):
        ]

        if " to " not in text:

            return (
                "Use: rename file "
                "OLD to NEW"
            )

        old, new = (
            text.split(
                " to ",
                1
            )
        )

        return rename_item(
            old,
            new
        )

    # =====================================================
    # MOVE TO KNOWN LOCATION
    # =====================================================

    if (
        command.startswith(
            "move folder "
        )
        or
        command.startswith(
            "move file "
        )
    ):

        text = (
            command.split(
                " ",
                2
            )[2]
        )

        if " to " not in text:

            return (
                "Use: move file/folder "
                "NAME to LOCATION"
            )

        name, destination = (
            text.rsplit(
                " to ",
                1
            )
        )

        return move_item(
            name,
            destination
        )

    # =====================================================
    # COPY TO KNOWN LOCATION
    # =====================================================

    if (
        command.startswith(
            "copy folder "
        )
        or
        command.startswith(
            "copy file "
        )
    ):

        text = (
            command.split(
                " ",
                2
            )[2]
        )

        if " to " not in text:

            return (
                "Use: copy file/folder "
                "NAME to LOCATION"
            )

        name, destination = (
            text.rsplit(
                " to ",
                1
            )
        )

        return copy_item(
            name,
            destination
        )

    # =====================================================
    # FIND ANYWHERE
    # =====================================================

    if command.startswith(
        "find "
    ):

        name = command[
            len("find "):
        ].strip()

        found = find_item(
            name
        )

        if found:

            return (
                f"Found: {found}"
            )

        return (
            f"I couldn't find "
            f"'{name}' on this computer."
        )

    # =====================================================
    # OPEN FILE ANYWHERE
    # =====================================================

    if command.startswith(
        "open file "
    ):

        name = command[
            len("open file "):
        ].strip()

        return open_file_or_folder(
            name,
            only_file=True
        )

    # =====================================================
    # OPEN FOLDER ANYWHERE
    # =====================================================

    if command.startswith(
        "open folder "
    ):

        name = command[
            len("open folder "):
        ].strip()

        return open_file_or_folder(
            name,
            only_folder=True
        )

    # =====================================================
    # CLOSE APPLICATION
    # =====================================================

    for prefix in [
        "close ",
        "quit ",
        "exit ",
    ]:

        if command.startswith(
            prefix
        ):

            app_name = command[
                len(prefix):
            ].strip()

            if not app_name:

                return (
                    "Please tell me which "
                    "app to close."
                )

            return close_app(
                app_name
            )

    # =====================================================
    # APP RUNNING STATUS
    # =====================================================

    if (
        command.startswith(
            "is "
        )
        and
        command.endswith(
            " running"
        )
    ):

        app_name = command[
            len("is "):
            -len(" running")
        ].strip()

        if not app_name:

            return (
                "Please tell me which "
                "app to check."
            )

        if is_app_running(
            app_name
        ):

            return (
                f"{app_name.title()} "
                "is running."
            )

        return (
            f"{app_name.title()} "
            "is not running."
        )

    # =====================================================
    # OPEN APPLICATION
    # =====================================================

    for prefix in [
        "open ",
        "launch ",
        "start ",
    ]:

        if command.startswith(
            prefix
        ):

            app_name = command[
                len(prefix):
            ].strip()

            if not app_name:

                return (
                    "Please tell me which "
                    "app to open."
                )

            return open_app(
                app_name
            )

    return (
        "I don't know this command yet."
    )