from pathlib import Path
from datetime import datetime

from PIL import ImageGrab


# =========================================================
# SCREEN VISION STORAGE
# =========================================================

def get_vision_folder():

    folder = (
        Path.home()
        / "Pictures"
        / "WizzArc Vision"
    )

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    return folder


# =========================================================
# SAFE NAME
# =========================================================

def make_safe_name(
    name
):

    name = (
        str(name)
        .strip()
    )

    if not name:

        return None

    invalid = '<>:"/\\|?*'

    for char in invalid:

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
# AUTO NAME
# =========================================================

def generate_capture_name():

    stamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    return (
        f"vision_{stamp}.png"
    )


# =========================================================
# CAPTURE FULL SCREEN
# =========================================================

def capture_screen(
    filename=None
):

    folder = get_vision_folder()

    if filename:

        filename = make_safe_name(
            filename
        )

        if not filename:

            return (
                None,
                "Invalid capture name."
            )

    else:

        filename = (
            generate_capture_name()
        )

    target = (
        folder
        / filename
    )

    counter = 2

    while target.exists():

        target = (
            folder
            / (
                f"{Path(filename).stem}_"
                f"{counter}.png"
            )
        )

        counter += 1

    try:

        image = ImageGrab.grab()

        image.save(
            target
        )

        return (
            target,
            None
        )

    except Exception as error:

        return (
            None,
            f"Couldn't capture screen: {error}"
        )


# =========================================================
# CAPTURE REGION
# =========================================================

def capture_region(
    x,
    y,
    width,
    height,
    filename=None
):

    try:

        x = int(x)
        y = int(y)
        width = int(width)
        height = int(height)

    except (
        TypeError,
        ValueError,
    ):

        return (
            None,
            "Region values must be numbers."
        )

    if (
        width <= 0
        or
        height <= 0
    ):

        return (
            None,
            "Region width and height must be greater than 0."
        )

    left = x
    top = y
    right = (
        x
        + width
    )
    bottom = (
        y
        + height
    )

    folder = get_vision_folder()

    if filename:

        filename = make_safe_name(
            filename
        )

        if not filename:

            return (
                None,
                "Invalid capture name."
            )

    else:

        filename = (
            "region_"
            + datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            + ".png"
        )

    target = (
        folder
        / filename
    )

    counter = 2

    while target.exists():

        target = (
            folder
            / (
                f"{Path(filename).stem}_"
                f"{counter}.png"
            )
        )

        counter += 1

    try:

        image = ImageGrab.grab(
            bbox=(
                left,
                top,
                right,
                bottom
            )
        )

        image.save(
            target
        )

        return (
            target,
            None
        )

    except Exception as error:

        return (
            None,
            f"Couldn't capture region: {error}"
        )


# =========================================================
# GET SCREEN SIZE
# =========================================================

def get_screen_dimensions():

    try:

        image = ImageGrab.grab()

        width, height = (
            image.size
        )

        return (
            width,
            height,
            None
        )

    except Exception as error:

        return (
            None,
            None,
            f"Couldn't read screen size: {error}"
        )


# =========================================================
# SCREEN INFO TEXT
# =========================================================

def get_screen_info():

    width, height, error = (
        get_screen_dimensions()
    )

    if error:

        return error

    return (
        f"Screen size is "
        f"{width} by {height} pixels."
    )