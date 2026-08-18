import os
import re
import shutil
import string
from pathlib import Path


# =========================================================
# AVAILABLE DRIVES
# =========================================================

def get_available_drives():

    drives = []

    for letter in string.ascii_uppercase:

        drive = Path(
            f"{letter}:\\"
        )

        try:

            if drive.exists():
                drives.append(
                    drive
                )

        except OSError:
            continue

    return drives


# =========================================================
# NORMALIZE DRIVE NAME
# =========================================================

def normalize_drive_name(
    drive_name
):

    drive_name = (
        str(drive_name)
        .lower()
        .strip()
    )

    for old in [
        " drive",
        "drive ",
        ":",
        "\\",
        "/",
    ]:

        drive_name = (
            drive_name.replace(
                old,
                ""
            )
        )

    drive_name = (
        drive_name
        .strip()
        .upper()
    )

    if (
        len(drive_name) == 1
        and
        drive_name.isalpha()
    ):

        return Path(
            f"{drive_name}:\\"
        )

    return None


# =========================================================
# NORMALIZE ITEM NAME
# =========================================================

def normalize_item_name(
    name
):

    return re.sub(
        r"[^a-z0-9]+",
        "",
        str(name)
        .lower()
        .strip()
    )


# =========================================================
# LIST DRIVE ITEMS
# =========================================================

def list_drive_items(
    drive_name,
    folders_only=False,
    files_only=False
):

    drive = normalize_drive_name(
        drive_name
    )

    if drive is None:

        return (
            None,
            "Invalid drive name."
        )

    if not drive.exists():

        return (
            None,
            f"Drive {drive} was not found."
        )

    items = []

    try:

        for item in drive.iterdir():

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

            except (
                PermissionError,
                OSError,
            ):
                continue

    except PermissionError:

        return (
            None,
            (
                f"WizzArc doesn't have permission "
                f"to access {drive}."
            )
        )

    except OSError as error:

        return (
            None,
            f"Couldn't access {drive}: {error}"
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
# DRIVE LIST TEXT
# =========================================================

def get_drive_list_text():

    drives = get_available_drives()

    if not drives:

        return (
            "No accessible drives found."
        )

    lines = [
        "Available drives:"
    ]

    for drive in drives:

        lines.append(
            str(drive)
        )

    return "\n".join(
        lines
    )


# =========================================================
# DRIVE ITEMS TEXT
# =========================================================

def get_drive_items_text(
    drive_name,
    folders_only=False,
    files_only=False
):

    items, error = list_drive_items(
        drive_name,
        folders_only=folders_only,
        files_only=files_only
    )

    if error:
        return error

    if not items:

        return (
            "No matching items found."
        )

    lines = []

    for item in items:

        try:

            if item.is_dir():

                item_type = "Folder"

            else:

                item_type = "File"

            lines.append(
                f"[{item_type}] {item.name}"
            )

        except OSError:
            continue

    return "\n".join(
        lines
    )


# =========================================================
# SHOULD SKIP DIRECTORY
# =========================================================

def should_skip_directory(
    path
):

    try:

        name = (
            path.name
            .lower()
            .strip()
        )

    except Exception:
        return True

    skipped_names = {
        "$recycle.bin",
        "system volume information",
        "windows",
        "winsxs",
        "programdata",
        "appdata",
        "node_modules",
        ".git",
        "__pycache__",
    }

    return (
        name
        in skipped_names
    )


# =========================================================
# SEARCH ONE DRIVE
# =========================================================

def search_drive(
    drive,
    name,
    only_folder=False,
    only_file=False,
    max_results=20
):

    drive = Path(
        drive
    )

    search_name = (
        str(name)
        .lower()
        .strip()
    )

    normalized_search = (
        normalize_item_name(
            name
        )
    )

    if not search_name:
        return []

    exact_results = []
    partial_results = []

    try:

        for root, dirs, files in os.walk(
            drive,
            topdown=True
        ):

            root_path = Path(
                root
            )

            # =============================================
            # REMOVE SKIPPED DIRECTORIES
            # =============================================

            safe_dirs = []

            for directory in dirs:

                path = (
                    root_path
                    / directory
                )

                if should_skip_directory(
                    path
                ):
                    continue

                safe_dirs.append(
                    directory
                )

            dirs[:] = safe_dirs

            # =============================================
            # SEARCH FOLDERS
            # =============================================

            if not only_file:

                for directory in dirs:

                    path = (
                        root_path
                        / directory
                    )

                    directory_lower = (
                        directory
                        .lower()
                    )

                    normalized_directory = (
                        normalize_item_name(
                            directory
                        )
                    )

                    if (
                        directory_lower
                        == search_name
                        or
                        (
                            normalized_search
                            and
                            normalized_directory
                            == normalized_search
                        )
                    ):

                        exact_results.append(
                            path
                        )

                    elif (
                        search_name
                        in directory_lower
                    ):

                        partial_results.append(
                            path
                        )

                    if (
                        len(exact_results)
                        >= max_results
                    ):

                        return exact_results[
                            :max_results
                        ]

            # =============================================
            # SEARCH FILES
            # =============================================

            if not only_folder:

                for filename in files:

                    path = (
                        root_path
                        / filename
                    )

                    filename_lower = (
                        filename
                        .lower()
                    )

                    normalized_filename = (
                        normalize_item_name(
                            filename
                        )
                    )

                    if (
                        filename_lower
                        == search_name
                        or
                        (
                            normalized_search
                            and
                            normalized_filename
                            == normalized_search
                        )
                    ):

                        exact_results.append(
                            path
                        )

                    elif (
                        search_name
                        in filename_lower
                    ):

                        partial_results.append(
                            path
                        )

                    if (
                        len(exact_results)
                        >= max_results
                    ):

                        return exact_results[
                            :max_results
                        ]

    except (
        PermissionError,
        OSError,
    ):
        pass

    if exact_results:

        return exact_results[
            :max_results
        ]

    return partial_results[
        :max_results
    ]


# =========================================================
# SEARCH ALL DRIVES
# =========================================================

def search_all_drives(
    name,
    only_folder=False,
    only_file=False,
    max_results=20
):

    results = []

    for drive in get_available_drives():

        found = search_drive(
            drive,
            name,
            only_folder=only_folder,
            only_file=only_file,
            max_results=max_results
        )

        results.extend(
            found
        )

        if (
            len(results)
            >= max_results
        ):
            break

    return results[
        :max_results
    ]


# =========================================================
# FIND FIRST ITEM ALL DRIVES
# =========================================================

def find_item_all_drives(
    name,
    only_folder=False,
    only_file=False
):

    results = search_all_drives(
        name,
        only_folder=only_folder,
        only_file=only_file,
        max_results=1
    )

    if results:

        return results[0]

    return None


# =========================================================
# FIND ITEM IN SPECIFIC DRIVE
# =========================================================

def find_item_in_drive(
    name,
    drive_name,
    only_folder=False,
    only_file=False
):

    drive = normalize_drive_name(
        drive_name
    )

    if (
        drive is None
        or
        not drive.exists()
    ):

        return None

    results = search_drive(
        drive,
        name,
        only_folder=only_folder,
        only_file=only_file,
        max_results=1
    )

    if results:

        return results[0]

    return None


# =========================================================
# SEARCH DRIVE TEXT
# =========================================================

def search_drive_text(
    name,
    drive_name,
    only_folder=False,
    only_file=False
):

    drive = normalize_drive_name(
        drive_name
    )

    if drive is None:

        return (
            "Invalid drive name."
        )

    if not drive.exists():

        return (
            f"{str(drive_name).upper()} "
            "drive was not found."
        )

    results = search_drive(
        drive,
        name,
        only_folder=only_folder,
        only_file=only_file,
        max_results=20
    )

    if not results:

        return (
            f"I couldn't find '{name}' "
            f"in {str(drive_name).upper()} drive."
        )

    lines = [
        (
            f"Found {len(results)} "
            f"result(s) in "
            f"{str(drive_name).upper()} drive:"
        )
    ]

    for item in results:

        lines.append(
            str(item)
        )

    return "\n".join(
        lines
    )


# =========================================================
# OPEN ITEM IN SPECIFIC DRIVE
# =========================================================

def open_item_in_drive(
    name,
    drive_name,
    only_folder=False,
    only_file=False
):

    item = find_item_in_drive(
        name,
        drive_name,
        only_folder=only_folder,
        only_file=only_file
    )

    if not item:

        return (
            f"I couldn't find '{name}' "
            f"in {str(drive_name).upper()} drive."
        )

    try:

        os.startfile(
            str(item)
        )

        return (
            f"{item.name} opened."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to open '{item.name}'."
        )

    except OSError as error:

        return (
            f"Couldn't open "
            f"'{item.name}'. "
            f"Windows error: {error}"
        )

    except Exception as error:

        return (
            f"Couldn't open "
            f"'{item.name}': {error}"
        )


# =========================================================
# CREATE FOLDER IN DRIVE
# =========================================================

def create_folder_in_drive(
    folder_name,
    drive_name
):

    drive = normalize_drive_name(
        drive_name
    )

    if drive is None:

        return (
            "Invalid drive name."
        )

    if not drive.exists():

        return (
            f"{str(drive_name).upper()} "
            "drive was not found."
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
        drive
        / folder_name
    )

    if target.exists():

        return (
            f"'{folder_name}' "
            f"already exists in "
            f"{str(drive_name).upper()} drive."
        )

    try:

        target.mkdir()

        return (
            f"Folder '{folder_name}' "
            f"created in "
            f"{str(drive_name).upper()} drive."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to create folders directly in "
            f"{str(drive_name).upper()} drive. "
            "Try Documents, Downloads, Desktop, "
            "or another writable folder."
        )

    except OSError as error:

        return (
            f"Couldn't create folder "
            f"'{folder_name}'. "
            f"Windows error: {error}"
        )

    except Exception as error:

        return (
            f"Couldn't create folder: "
            f"{error}"
        )


# =========================================================
# MOVE TO DRIVE
# =========================================================

def move_item_to_drive(
    item,
    drive_name
):

    drive = normalize_drive_name(
        drive_name
    )

    if drive is None:

        return (
            "Invalid drive name."
        )

    if not drive.exists():

        return (
            f"{str(drive_name).upper()} "
            "drive was not found."
        )

    item = Path(
        item
    )

    if not item.exists():

        return (
            f"'{item.name}' "
            "was not found."
        )

    target = (
        drive
        / item.name
    )

    if target.exists():

        return (
            f"'{item.name}' already exists "
            f"in {str(drive_name).upper()} drive."
        )

    try:

        shutil.move(
            str(item),
            str(target)
        )

        return (
            f"Moved '{item.name}' to "
            f"{str(drive_name).upper()} drive."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to move '{item.name}' directly "
            f"to {str(drive_name).upper()} drive. "
            "Try Documents, Downloads, Desktop, "
            "or another writable folder."
        )

    except OSError as error:

        return (
            f"Couldn't move '{item.name}'. "
            f"Windows error: {error}"
        )

    except Exception as error:

        return (
            f"Couldn't move item: "
            f"{error}"
        )


# =========================================================
# COPY TO DRIVE
# =========================================================

def copy_item_to_drive(
    item,
    drive_name
):

    drive = normalize_drive_name(
        drive_name
    )

    if drive is None:

        return (
            "Invalid drive name."
        )

    if not drive.exists():

        return (
            f"{str(drive_name).upper()} "
            "drive was not found."
        )

    item = Path(
        item
    )

    if not item.exists():

        return (
            f"'{item.name}' "
            "was not found."
        )

    target = (
        drive
        / item.name
    )

    if target.exists():

        return (
            f"'{item.name}' already exists "
            f"in {str(drive_name).upper()} drive."
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
            f"Copied '{item.name}' to "
            f"{str(drive_name).upper()} drive."
        )

    except PermissionError:

        return (
            f"WizzArc doesn't have permission "
            f"to copy '{item.name}' directly "
            f"to {str(drive_name).upper()} drive. "
            "Try Documents, Downloads, Desktop, "
            "or another writable folder."
        )

    except OSError as error:

        return (
            f"Couldn't copy '{item.name}'. "
            f"Windows error: {error}"
        )

    except Exception as error:

        return (
            f"Couldn't copy item: "
            f"{error}"
        )