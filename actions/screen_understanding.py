import re
import hashlib
from datetime import datetime, timedelta

from PIL import ImageGrab
import pytesseract


TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = (
    TESSERACT_PATH
)


# =========================================================
# SCREEN SNAPSHOT CACHE
# =========================================================

SCREEN_SNAPSHOT = {
    "created_at": None,
    "elements": [],
    "clickable": [],
    "fingerprint": None,
}


# Snapshot lifetime in seconds.
# After this time, WizzArc will refresh before using numbered elements.
SCREEN_SNAPSHOT_MAX_AGE = 20


# =========================================================
# BASIC TEXT CLEANUP
# =========================================================

def clean_detected_text(
    text
):

    text = (
        str(text)
        .strip()
    )

    if not text:

        return ""

    # Remove repeated outer punctuation/noise while
    # keeping useful filename characters such as _ . -
    text = re.sub(
        r"^[^\w]+|[^\w.()_\-]+$",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# USEFUL TEXT CHECK
# =========================================================

def is_useful_text(
    text,
    confidence,
    minimum_confidence=45
):

    if confidence < minimum_confidence:

        return False

    text = clean_detected_text(
        text
    )

    if not text:

        return False

    # Single punctuation / symbol noise
    if not re.search(
        r"[A-Za-z0-9]",
        text
    ):

        return False

    # Ignore tiny one-character OCR noise except useful
    # menu/drive-like tokens such as C.
    if (
        len(text) == 1
        and
        not text.isalnum()
    ):

        return False

    noisy_tokens = {
        "od",
        "ua",
        "yy",
    }

    if (
        text.lower()
        in noisy_tokens
    ):

        return False

    return True


# =========================================================
# CLASSIFY ELEMENT
# =========================================================

def classify_element(
    text
):

    lower = (
        text
        .lower()
        .strip()
    )

    menu_words = {
        "file",
        "edit",
        "selection",
        "view",
        "go",
        "run",
        "terminal",
        "help",
    }

    if lower in menu_words:

        return "menu"

    if lower.endswith(
        (
            ".py",
            ".txt",
            ".json",
            ".html",
            ".css",
            ".js",
            ".md",
        )
    ):

        return "file"

    if lower in {
        "settings",
        "downloads",
        "documents",
        "explorer",
        "search",
        "source control",
        "extensions",
    }:

        return "label"

    if (
        len(text) <= 24
        and
        re.fullmatch(
            r"[A-Za-z0-9 _.\-()]+",
            text
        )
    ):

        return "likely_clickable"

    return "text"


# =========================================================
# SCAN SCREEN ELEMENTS
# =========================================================

def scan_screen_elements(
    minimum_confidence=45
):

    try:

        image = ImageGrab.grab()

        data = pytesseract.image_to_data(
            image,
            output_type=(
                pytesseract.Output.DICT
            )
        )

        elements = []

        count = len(
            data["text"]
        )

        for index in range(
            count
        ):

            raw_text = (
                str(
                    data["text"][index]
                )
                .strip()
            )

            confidence_raw = (
                data["conf"][index]
            )

            try:

                confidence = float(
                    confidence_raw
                )

            except (
                TypeError,
                ValueError,
            ):

                confidence = -1

            text = clean_detected_text(
                raw_text
            )

            if not is_useful_text(
                text,
                confidence,
                minimum_confidence
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

            elements.append(
                {
                    "text":
                        text,

                    "confidence":
                        confidence,

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

                    "type":
                        classify_element(
                            text
                        ),
                }
            )

        return (
            elements,
            None
        )

    except Exception as error:

        return (
            [],
            (
                "Couldn't understand the screen: "
                f"{error}"
            )
        )


# =========================================================
# DEDUPLICATE ELEMENTS
# =========================================================

def deduplicate_elements(
    elements
):

    unique = []
    seen = set()

    for element in elements:

        key = (
            element["text"]
            .lower()
            .strip(),
            round(
                element["center_x"]
                / 20
            ),
            round(
                element["center_y"]
                / 20
            ),
        )

        if key in seen:

            continue

        seen.add(
            key
        )

        unique.append(
            element
        )

    return unique


# =========================================================
# SCREEN SUMMARY
# =========================================================

def get_screen_summary():

    elements, error = (
        scan_screen_elements()
    )

    if error:

        return error

    elements = deduplicate_elements(
        elements
    )

    if not elements:

        return (
            "I couldn't detect any useful "
            "visible screen elements."
        )

    # Prefer useful UI-like elements in preview.
    preferred = [
        element
        for element in elements
        if element[
            "type"
        ] in {
            "menu",
            "file",
            "label",
            "likely_clickable",
        }
    ]

    source = (
        preferred
        if preferred
        else elements
    )

    preview = []

    seen_text = set()

    for element in source:

        lower = (
            element["text"]
            .lower()
        )

        if lower in seen_text:

            continue

        seen_text.add(
            lower
        )

        preview.append(
            element["text"]
        )

        if len(
            preview
        ) >= 35:

            break

    return (
        f"I can see {len(elements)} "
        f"useful screen elements. "
        f"Some visible items are: "
        + ", ".join(
            preview
        )
    )


# =========================================================
# SHOW VISIBLE ELEMENTS
# =========================================================

def show_visible_elements(
    limit=50
):

    elements, error = (
        scan_screen_elements()
    )

    if error:

        return error

    elements = deduplicate_elements(
        elements
    )

    if not elements:

        return (
            "No useful visible screen "
            "elements found."
        )

    try:

        limit = int(
            limit
        )

    except (
        TypeError,
        ValueError,
    ):

        limit = 50

    limit = max(
        1,
        min(
            limit,
            100
        )
    )

    lines = [
        (
            f"Visible elements "
            f"({len(elements)} useful detected):"
        )
    ]

    for index, element in enumerate(
        elements[:limit],
        start=1
    ):

        lines.append(
            (
                f"{index}. "
                f"{element['text']} "
                f"[{element['type']}] "
                f"at "
                f"{element['center_x']}, "
                f"{element['center_y']} "
                f"(confidence "
                f"{element['confidence']:.0f}%)"
            )
        )

    return "\n".join(
        lines
    )


# =========================================================
# SHOW LIKELY CLICKABLE ELEMENTS
# =========================================================

def show_clickable_elements(
    limit=50
):

    elements, error = (
        scan_screen_elements()
    )

    if error:

        return error

    elements = deduplicate_elements(
        elements
    )

    clickable = [
        element
        for element in elements
        if element[
            "type"
        ] in {
            "menu",
            "label",
            "likely_clickable",
        }
    ]

    if not clickable:

        return (
            "I couldn't identify any likely "
            "clickable text elements."
        )

    try:

        limit = int(
            limit
        )

    except (
        TypeError,
        ValueError,
    ):

        limit = 50

    limit = max(
        1,
        min(
            limit,
            100
        )
    )

    lines = [
        (
            f"Likely clickable elements "
            f"({len(clickable)} detected):"
        )
    ]

    for index, element in enumerate(
        clickable[:limit],
        start=1
    ):

        lines.append(
            (
                f"{index}. "
                f"{element['text']} "
                f"at "
                f"{element['center_x']}, "
                f"{element['center_y']}"
            )
        )

    return "\n".join(
        lines
    )


# =========================================================
# IS TEXT VISIBLE
# =========================================================

def is_text_visible(
    search_text
):

    search_text = (
        str(search_text)
        .strip()
        .lower()
    )

    if not search_text:

        return (
            "Please tell me what to look for."
        )

    elements, error = (
        scan_screen_elements()
    )

    if error:

        return error

    elements = deduplicate_elements(
        elements
    )

    matches = [
        element
        for element in elements
        if search_text
        in element[
            "text"
        ].lower()
    ]

    if not matches:

        return (
            f"No, I can't see "
            f"'{search_text}' "
            "on the screen."
        )

    return (
        f"Yes, '{search_text}' "
        f"is visible "
        f"{len(matches)} time"
        f"{'s' if len(matches) != 1 else ''}."
    )


# =========================================================
# WHERE IS TEXT
# =========================================================

def where_is_text(
    search_text
):

    search_text = (
        str(search_text)
        .strip()
        .lower()
    )

    if not search_text:

        return (
            "Please tell me what to locate."
        )

    elements, error = (
        scan_screen_elements()
    )

    if error:

        return error

    elements = deduplicate_elements(
        elements
    )

    matches = [
        element
        for element in elements
        if search_text
        in element[
            "text"
        ].lower()
    ]

    if not matches:

        return (
            f"I couldn't find "
            f"'{search_text}' "
            "on the screen."
        )

    lines = [
        (
            f"I found "
            f"{len(matches)} match"
            f"{'es' if len(matches) != 1 else ''} "
            f"for '{search_text}':"
        )
    ]

    for match in matches:

        lines.append(
            (
                f"{match['text']} "
                f"[{match['type']}] "
                f"at "
                f"{match['center_x']}, "
                f"{match['center_y']}"
            )
        )

    return "\n".join(
        lines
    )

# =========================================================
# SCREEN FINGERPRINT / CHANGE SAFETY
# =========================================================

def get_screen_fingerprint():
    try:
        image = ImageGrab.grab().convert("L").resize((64, 36))
        return hashlib.sha256(image.tobytes()).hexdigest()
    except Exception:
        return None


def has_screen_changed():
    old = SCREEN_SNAPSHOT.get("fingerprint")
    if not old:
        return True

    new = get_screen_fingerprint()
    if not new:
        return False

    return new != old


def get_screen_change_status():
    if SCREEN_SNAPSHOT.get("created_at") is None:
        return "No screen snapshot is currently cached."

    if has_screen_changed():
        return "The screen has changed since the cached snapshot."

    return "The screen still matches the cached snapshot."


# =========================================================
# GET SNAPSHOT AGE
# =========================================================

def get_screen_snapshot_age():

    created_at = SCREEN_SNAPSHOT.get(
        "created_at"
    )

    if created_at is None:

        return None

    return (
        datetime.now()
        - created_at
    ).total_seconds()


# =========================================================
# SNAPSHOT EXPIRED?
# =========================================================

def is_screen_snapshot_expired(
    max_age_seconds=None
):

    if max_age_seconds is None:

        max_age_seconds = (
            SCREEN_SNAPSHOT_MAX_AGE
        )

    try:

        max_age_seconds = float(
            max_age_seconds
        )

    except (
        TypeError,
        ValueError,
    ):

        max_age_seconds = (
            SCREEN_SNAPSHOT_MAX_AGE
        )

    age = get_screen_snapshot_age()

    if age is None:

        return True

    return (
        age > max_age_seconds
    )


# =========================================================
# SCREEN SNAPSHOT STATUS
# =========================================================

def get_screen_snapshot_status():

    created_at = SCREEN_SNAPSHOT.get(
        "created_at"
    )

    clickable_count = len(
        SCREEN_SNAPSHOT.get(
            "clickable",
            []
        )
    )

    if created_at is None:

        return (
            "No screen snapshot is currently cached."
        )

    age = get_screen_snapshot_age()

    expired = is_screen_snapshot_expired()

    return (
        f"Screen snapshot age: "
        f"{age:.1f} seconds. "
        f"Clickable elements: "
        f"{clickable_count}. "
        f"Status: "
        f"{'expired' if expired else 'fresh'}."
    )


# =========================================================
# REFRESH SCREEN SNAPSHOT
# =========================================================

def refresh_screen_snapshot():

    elements, error = (
        scan_screen_elements()
    )

    if error:

        return error

    elements = deduplicate_elements(
        elements
    )

    clickable = [
        element
        for element in elements
        if element[
            "type"
        ] in {
            "menu",
            "label",
            "likely_clickable",
        }
    ]

    SCREEN_SNAPSHOT[
        "created_at"
    ] = datetime.now()

    SCREEN_SNAPSHOT[
        "elements"
    ] = elements

    SCREEN_SNAPSHOT[
        "clickable"
    ] = clickable

    SCREEN_SNAPSHOT[
        "fingerprint"
    ] = get_screen_fingerprint()

    return (
        f"Screen snapshot refreshed. "
        f"{len(elements)} useful elements and "
        f"{len(clickable)} clickable elements cached."
    )


# =========================================================
# CLEAR SCREEN SNAPSHOT
# =========================================================

def clear_screen_snapshot():

    SCREEN_SNAPSHOT[
        "created_at"
    ] = None

    SCREEN_SNAPSHOT[
        "elements"
    ] = []

    SCREEN_SNAPSHOT[
        "clickable"
    ] = []

    SCREEN_SNAPSHOT[
        "fingerprint"
    ] = None

    return (
        "Screen snapshot cleared."
    )


# =========================================================
# ENSURE SCREEN SNAPSHOT
# =========================================================

def ensure_screen_snapshot(
    auto_refresh=True
):

    has_clickable = bool(
        SCREEN_SNAPSHOT["clickable"]
    )

    expired = is_screen_snapshot_expired()

    changed = (
        has_screen_changed()
        if has_clickable
        else True
    )

    if has_clickable and not expired and not changed:
        return None

    if not auto_refresh:
        if not has_clickable:
            return "No screen snapshot is cached."
        if expired:
            return (
                "The screen snapshot is stale. "
                "Refresh it before using numbered elements."
            )
        return (
            "The screen has changed since the snapshot. "
            "Refresh it before using numbered elements."
        )

    result = refresh_screen_snapshot()

    if not SCREEN_SNAPSHOT["clickable"]:
        return result

    return None

# =========================================================
# GET SNAPSHOT CLICKABLE ELEMENTS
# =========================================================

def get_snapshot_clickable_elements():

    error = ensure_screen_snapshot(
        auto_refresh=True
    )

    if (
        error
        and
        not SCREEN_SNAPSHOT[
            "clickable"
        ]
    ):

        return (
            [],
            error
        )

    return (
        list(
            SCREEN_SNAPSHOT[
                "clickable"
            ]
        ),
        None
    )

# =========================================================
# SHOW SNAPSHOT CLICKABLE ELEMENTS
# =========================================================

def show_snapshot_clickable_elements(
    limit=50
):

    clickable, error = (
        get_snapshot_clickable_elements()
    )

    if error:

        return error

    try:

        limit = int(
            limit
        )

    except (
        TypeError,
        ValueError,
    ):

        limit = 50

    limit = max(
        1,
        min(
            limit,
            100
        )
    )

    created_at = (
        SCREEN_SNAPSHOT.get(
            "created_at"
        )
    )

    created_text = (
        created_at.strftime(
            "%I:%M:%S %p"
        )
        if created_at
        else "unknown"
    )

    lines = [
        (
            f"Cached clickable elements "
            f"({len(clickable)} detected, "
            f"snapshot {created_text}):"
        )
    ]

    for index, element in enumerate(
        clickable[:limit],
        start=1
    ):

        lines.append(
            (
                f"{index}. "
                f"{element['text']} "
                f"at "
                f"{element['center_x']}, "
                f"{element['center_y']}"
            )
        )

    return "\n".join(
        lines
    )


# =========================================================
# GET CLICKABLE ELEMENTS
# =========================================================

def get_clickable_elements():

    elements, error = (
        scan_screen_elements()
    )

    if error:

        return (
            [],
            error
        )

    elements = deduplicate_elements(
        elements
    )

    clickable = [
        element
        for element in elements
        if element[
            "type"
        ] in {
            "menu",
            "label",
            "likely_clickable",
        }
    ]

    return (
        clickable,
        None
    )


# =========================================================
# GET CLICKABLE ELEMENT POSITION
# =========================================================

def get_clickable_element_position(
    number
):

    try:

        number = int(
            number
        )

    except (
        TypeError,
        ValueError,
    ):

        return (
            None,
            None,
            None,
            "Element number must be a number."
        )

    if number <= 0:

        return (
            None,
            None,
            None,
            "Element number must be greater than 0."
        )

    clickable, error = (
        get_snapshot_clickable_elements()
    )

    if error:

        return (
            None,
            None,
            None,
            error
        )

    if not clickable:

        return (
            None,
            None,
            None,
            "No clickable elements were detected."
        )

    index = (
        number
        - 1
    )

    if index >= len(
        clickable
    ):

        return (
            None,
            None,
            None,
            (
                f"I found only "
                f"{len(clickable)} clickable "
                f"element"
                f"{'s' if len(clickable) != 1 else ''}."
            )
        )

    element = clickable[
        index
    ]

    return (
        element[
            "center_x"
        ],
        element[
            "center_y"
        ],
        element[
            "text"
        ],
        None
    )

# =========================================================
# GROUP ELEMENTS BY SCREEN REGION
# =========================================================

def group_elements_by_region(
    elements=None
):

    if elements is None:

        elements, error = (
            scan_screen_elements()
        )

        if error:

            return (
                {},
                error
            )

        elements = deduplicate_elements(
            elements
        )

    try:

        image = ImageGrab.grab()

        screen_width, screen_height = (
            image.size
        )

    except Exception as error:

        return (
            {},
            (
                "Couldn't read screen size for "
                f"context grouping: {error}"
            )
        )

    groups = {
        "top_left": [],
        "top_center": [],
        "top_right": [],
        "middle_left": [],
        "middle_center": [],
        "middle_right": [],
        "bottom_left": [],
        "bottom_center": [],
        "bottom_right": [],
    }

    for element in elements:

        x = element[
            "center_x"
        ]

        y = element[
            "center_y"
        ]

        if x < screen_width / 3:

            horizontal = "left"

        elif x < (
            screen_width
            * 2 / 3
        ):

            horizontal = "center"

        else:

            horizontal = "right"

        if y < screen_height / 3:

            vertical = "top"

        elif y < (
            screen_height
            * 2 / 3
        ):

            vertical = "middle"

        else:

            vertical = "bottom"

        key = (
            f"{vertical}_"
            f"{horizontal}"
        )

        groups[
            key
        ].append(
            element
        )

    return (
        groups,
        None
    )


# =========================================================
# BUILD NEARBY TEXT CONTEXT
# =========================================================

def get_nearby_text_context(
    search_text,
    radius=140
):

    search_text = (
        str(search_text)
        .strip()
        .lower()
    )

    if not search_text:

        return (
            "Please tell me which text "
            "you want context for."
        )

    elements, error = (
        scan_screen_elements()
    )

    if error:

        return error

    elements = deduplicate_elements(
        elements
    )

    matches = [
        element
        for element in elements
        if search_text
        in element[
            "text"
        ].lower()
    ]

    if not matches:

        return (
            f"I couldn't find "
            f"'{search_text}' "
            "on the screen."
        )

    try:

        radius = int(
            radius
        )

    except (
        TypeError,
        ValueError,
    ):

        radius = 140

    radius = max(
        40,
        min(
            radius,
            500
        )
    )

    lines = []

    for match_index, match in enumerate(
        matches,
        start=1
    ):

        nearby = []

        for element in elements:

            if element is match:

                continue

            dx = abs(
                element[
                    "center_x"
                ]
                - match[
                    "center_x"
                ]
            )

            dy = abs(
                element[
                    "center_y"
                ]
                - match[
                    "center_y"
                ]
            )

            if (
                dx <= radius
                and
                dy <= radius
            ):

                nearby.append(
                    element
                )

        nearby.sort(
            key=lambda item: (
                abs(
                    item[
                        "center_y"
                    ]
                    - match[
                        "center_y"
                    ]
                )
                +
                abs(
                    item[
                        "center_x"
                    ]
                    - match[
                        "center_x"
                    ]
                )
            )
        )

        preview = [
            item[
                "text"
            ]
            for item in nearby[
                :12
            ]
        ]

        lines.append(
            (
                f"Match {match_index}: "
                f"{match['text']} at "
                f"{match['center_x']}, "
                f"{match['center_y']}."
            )
        )

        if preview:

            lines.append(
                (
                    "Nearby context: "
                    + ", ".join(
                        preview
                    )
                )
            )

        else:

            lines.append(
                "Nearby context: none detected."
            )

    return "\n".join(
        lines
    )


# =========================================================
# SCREEN CONTEXT SUMMARY
# =========================================================

def get_screen_context_summary():

    elements, error = (
        scan_screen_elements()
    )

    if error:

        return error

    elements = deduplicate_elements(
        elements
    )

    groups, error = (
        group_elements_by_region(
            elements
        )
    )

    if error:

        return error

    lines = [
        (
            f"Screen context contains "
            f"{len(elements)} useful elements."
        )
    ]

    readable_names = {
        "top_left":
            "Top left",

        "top_center":
            "Top center",

        "top_right":
            "Top right",

        "middle_left":
            "Middle left",

        "middle_center":
            "Middle center",

        "middle_right":
            "Middle right",

        "bottom_left":
            "Bottom left",

        "bottom_center":
            "Bottom center",

        "bottom_right":
            "Bottom right",
    }

    for key, items in groups.items():

        if not items:

            continue

        preview = []

        seen = set()

        for item in items:

            text = item[
                "text"
            ]

            lower = (
                text
                .lower()
            )

            if lower in seen:

                continue

            seen.add(
                lower
            )

            preview.append(
                text
            )

            if len(
                preview
            ) >= 10:

                break

        lines.append(
            (
                f"{readable_names[key]}: "
                + ", ".join(
                    preview
                )
            )
        )

    return "\n".join(
        lines
    )
