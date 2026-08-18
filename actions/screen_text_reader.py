import pytesseract
from PIL import ImageGrab


# =========================================================
# TESSERACT PATH
# =========================================================

TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = (
    TESSERACT_PATH
)


# =========================================================
# READ FULL SCREEN
# =========================================================

def read_screen_text():

    try:

        image = ImageGrab.grab()

        text = pytesseract.image_to_string(
            image
        )

        text = (
            text
            .strip()
        )

        if not text:

            return (
                "I couldn't detect any readable "
                "text on the screen."
            )

        return text

    except Exception as error:

        return (
            f"Couldn't read screen text: "
            f"{error}"
        )


# =========================================================
# READ SCREEN REGION
# =========================================================

def read_region_text(
    x,
    y,
    width,
    height
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
            "Region values must be numbers."
        )

    if (
        width <= 0
        or
        height <= 0
    ):

        return (
            "Region width and height "
            "must be greater than 0."
        )

    bbox = (
        x,
        y,
        x + width,
        y + height
    )

    try:

        image = ImageGrab.grab(
            bbox=bbox
        )

        text = pytesseract.image_to_string(
            image
        )

        text = (
            text
            .strip()
        )

        if not text:

            return (
                "I couldn't detect readable "
                "text in that screen region."
            )

        return text

    except Exception as error:

        return (
            f"Couldn't read region text: "
            f"{error}"
        )


# =========================================================
# GET TEXT MATCHES ON SCREEN
# =========================================================

def get_text_matches_on_screen(
    search_text
):

    search_text = (
        str(search_text)
        .strip()
    )

    if not search_text:

        return (
            [],
            "Please tell me what text to find."
        )

    try:

        image = ImageGrab.grab()

        data = pytesseract.image_to_data(
            image,
            output_type=(
                pytesseract.Output.DICT
            )
        )

        search_lower = (
            search_text
            .lower()
        )

        matches = []

        count = len(
            data["text"]
        )

        for index in range(
            count
        ):

            word = (
                str(
                    data["text"][index]
                )
                .strip()
            )

            if not word:

                continue

            if (
                search_lower
                not in word.lower()
            ):

                continue

            x = int(
                data["left"][index]
            )

            y = int(
                data["top"][index]
            )

            width = int(
                data["width"][index]
            )

            height = int(
                data["height"][index]
            )

            center_x = (
                x
                + width // 2
            )

            center_y = (
                y
                + height // 2
            )

            matches.append(
                {
                    "text":
                        word,

                    "x":
                        x,

                    "y":
                        y,

                    "width":
                        width,

                    "height":
                        height,

                    "center_x":
                        center_x,

                    "center_y":
                        center_y,
                }
            )

        return (
            matches,
            None
        )

    except Exception as error:

        return (
            [],
            (
                "Couldn't find text on screen: "
                f"{error}"
            )
        )


# =========================================================
# FIND TEXT ON SCREEN
# =========================================================

def find_text_on_screen(
    search_text
):

    matches, error = (
        get_text_matches_on_screen(
            search_text
        )
    )

    if error:

        return error

    if not matches:

        return (
            f"I couldn't find "
            f"'{search_text}' "
            "on the screen."
        )

    lines = [
        (
            f"Found {len(matches)} "
            f"match"
            f"{'es' if len(matches) != 1 else ''}:"
        )
    ]

    for match in matches:

        lines.append(
            (
                f"{match['text']} "
                f"at {match['center_x']}, "
                f"{match['center_y']}"
            )
        )

    return "\n".join(
        lines
    )


# =========================================================
# GET FIRST TEXT POSITION
# =========================================================

def get_first_text_position(
    search_text
):

    matches, error = (
        get_text_matches_on_screen(
            search_text
        )
    )

    if error:

        return (
            None,
            None,
            error
        )

    if not matches:

        return (
            None,
            None,
            (
                f"I couldn't find "
                f"'{search_text}' "
                "on the screen."
            )
        )

    match = matches[0]

    return (
        match["center_x"],
        match["center_y"],
        None
    )

# =========================================================
# GET SELECTED TEXT POSITION
# =========================================================

def get_text_position(
    search_text,
    selector="first"
):

    matches, error = (
        get_text_matches_on_screen(
            search_text
        )
    )

    if error:

        return (
            None,
            None,
            error
        )

    if not matches:

        return (
            None,
            None,
            (
                f"I couldn't find "
                f"'{search_text}' "
                "on the screen."
            )
        )

    selector = (
        str(selector)
        .lower()
        .strip()
    )

    if selector == "first":

        index = 0

    elif selector == "last":

        index = (
            len(matches)
            - 1
        )

    elif selector == "second":

        index = 1

    elif selector == "third":

        index = 2

    else:

        try:

            index = (
                int(selector)
                - 1
            )

        except (
            TypeError,
            ValueError,
        ):

            return (
                None,
                None,
                (
                    "I couldn't understand "
                    "which match to select."
                )
            )

    if (
        index < 0
        or
        index >= len(matches)
    ):

        return (
            None,
            None,
            (
                f"I found only "
                f"{len(matches)} match"
                f"{'es' if len(matches) != 1 else ''} "
                f"for '{search_text}'."
            )
        )

    match = matches[
        index
    ]

    return (
        match[
            "center_x"
        ],
        match[
            "center_y"
        ],
        None
    )
