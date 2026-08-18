import re
from dataclasses import dataclass
from typing import Callable, Optional


# =========================================================
# COMMAND MODEL
# =========================================================

@dataclass
class CommandDefinition:
    command: str
    description: str
    category: str
    handler: Optional[Callable] = None
    aliases: tuple = ()


# =========================================================
# REGISTRY
# =========================================================

COMMANDS = []


# =========================================================
# REGISTER COMMAND
# =========================================================

def register_command(
    command,
    description,
    category,
    handler=None,
    aliases=None
):
    if aliases is None:
        aliases = []

    definition = CommandDefinition(
        command=command,
        description=description,
        category=category,
        handler=handler,
        aliases=tuple(aliases),
    )

    COMMANDS.append(definition)
    return definition


# =========================================================
# NORMALIZE
# =========================================================

def normalize_command_text(text):
    text = str(text).lower().strip()
    text = re.sub(r"[.,!?;:]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================================================
# TEMPLATE -> REGEX
# =========================================================

def template_to_regex(template):
    template = normalize_command_text(template)

    pattern = ""
    position = 0

    placeholder_pattern = re.compile(
        r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
    )

    matches = list(
        placeholder_pattern.finditer(template)
    )

    for match in matches:
        normal_text = template[
            position:match.start()
        ]

        pattern += re.escape(normal_text)

        placeholder_name = match.group(1)

        pattern += (
            rf"(?P<{placeholder_name}>.+?)"
        )

        position = match.end()

    pattern += re.escape(
        template[position:]
    )

    return "^" + pattern + "$"


# =========================================================
# BUILD COMMAND
# =========================================================

def build_command_from_template(
    template,
    values
):
    result = normalize_command_text(template)

    for name, value in values.items():
        result = result.replace(
            "{" + name + "}",
            value.strip()
        )

    return normalize_command_text(result)


# =========================================================
# MATCH DEFINITION
# =========================================================

def match_definition(
    text,
    definition
):
    text = normalize_command_text(text)
    template = normalize_command_text(
        definition.command
    )

    if "{" not in template:
        if text == template:
            return {
                "definition": definition,
                "command": template,
                "values": {},
            }

    else:
        pattern = template_to_regex(template)
        match = re.match(pattern, text)

        if match:
            values = {
                key: value.strip()
                for key, value
                in match.groupdict().items()
            }

            canonical = build_command_from_template(
                template,
                values
            )

            return {
                "definition": definition,
                "command": canonical,
                "values": values,
            }

    for alias in definition.aliases:
        alias = normalize_command_text(alias)

        if "{" in alias:
            pattern = template_to_regex(alias)
            match = re.match(pattern, text)

            if match:
                values = {
                    key: value.strip()
                    for key, value
                    in match.groupdict().items()
                }

                if (
                    definition.command
                    == "close {name}"
                    and
                    "name" in values
                ):
                    reserved = {
                        "wifi",
                        "wi-fi",
                        "bluetooth",
                    }

                    if (
                        values["name"]
                        .lower()
                        .strip()
                        in reserved
                    ):
                        continue

                canonical = build_command_from_template(
                    template,
                    values
                )

                return {
                    "definition": definition,
                    "command": canonical,
                    "values": values,
                }

        elif text == alias:
            return {
                "definition": definition,
                "command": template,
                "values": {},
            }

    return None


# =========================================================
# RESOLVE COMMAND
# =========================================================

def resolve_registered_command(text):
    text = normalize_command_text(text)

    if not text:
        return None

    # Exact commands and exact aliases first.
    for definition in COMMANDS:
        template = normalize_command_text(
            definition.command
        )

        if (
            "{" not in template
            and
            text == template
        ):
            return {
                "definition": definition,
                "command": template,
                "values": {},
            }

        for alias in definition.aliases:
            alias = normalize_command_text(alias)

            if (
                "{" not in alias
                and
                text == alias
            ):
                return {
                    "definition": definition,
                    "command": template,
                    "values": {},
                }

    # Dynamic commands.
    for definition in COMMANDS:
        result = match_definition(
            text,
            definition
        )

        if result is not None:
            return result

    return None


# =========================================================
# COMMAND GUIDE
# =========================================================

def get_commands_by_category():
    categories = {}

    for command in COMMANDS:
        categories.setdefault(
            command.category,
            []
        )

        categories[
            command.category
        ].append(command)

    return categories




# =========================================================
# AUTOMATION - PHASE 5
# =========================================================

register_command(
    "{command} after {seconds} seconds",
    "Runs a WizzArc command after a delay",
    "Automation",
)

register_command(
    "{command} after {seconds} second",
    "Runs a WizzArc command after a delay",
    "Automation",
)

register_command(
    "{command} after {minutes} minutes",
    "Runs a WizzArc command after a delay",
    "Automation",
)

register_command(
    "{command} after {minutes} minute",
    "Runs a WizzArc command after a delay",
    "Automation",
)

register_command(
    "{command} after {hours} hours",
    "Runs a WizzArc command after a delay",
    "Automation",
)

register_command(
    "{command} after {hours} hour",
    "Runs a WizzArc command after a delay",
    "Automation",
)


register_command(
    "{command} at {time}",
    "Runs a WizzArc command at a specific time",
    "Automation",
)




register_command(
    "{command} every {seconds} seconds for {duration} seconds",
    "Runs a WizzArc command repeatedly for a limited duration",
    "Automation",
)

register_command(
    "{command} every {seconds} seconds for {duration} minutes",
    "Runs a WizzArc command repeatedly for a limited duration",
    "Automation",
)

register_command(
    "{command} every {seconds} seconds for {duration} hours",
    "Runs a WizzArc command repeatedly for a limited duration",
    "Automation",
)

register_command(
    "{command} every {minutes} minutes for {duration} minutes",
    "Runs a WizzArc command repeatedly for a limited duration",
    "Automation",
)

register_command(
    "{command} every {minutes} minutes for {duration} hours",
    "Runs a WizzArc command repeatedly for a limited duration",
    "Automation",
)

register_command(
    "{command} every {hours} hours for {duration} hours",
    "Runs a WizzArc command repeatedly for a limited duration",
    "Automation",
)

register_command(
    "{command} every {seconds} seconds {count} times",
    "Runs a WizzArc command repeatedly for a fixed number of times",
    "Automation",
)

register_command(
    "{command} every {minutes} minutes {count} times",
    "Runs a WizzArc command repeatedly for a fixed number of times",
    "Automation",
)

register_command(
    "{command} every {hours} hours {count} times",
    "Runs a WizzArc command repeatedly for a fixed number of times",
    "Automation",
)

register_command(
    "{command} every {seconds} seconds",
    "Runs a WizzArc command repeatedly",
    "Automation",
)

register_command(
    "{command} every {seconds} second",
    "Runs a WizzArc command repeatedly",
    "Automation",
)

register_command(
    "{command} every {minutes} minutes",
    "Runs a WizzArc command repeatedly",
    "Automation",
)

register_command(
    "{command} every {minutes} minute",
    "Runs a WizzArc command repeatedly",
    "Automation",
)

register_command(
    "{command} every {hours} hours",
    "Runs a WizzArc command repeatedly",
    "Automation",
)

register_command(
    "{command} every {hours} hour",
    "Runs a WizzArc command repeatedly",
    "Automation",
)


register_command(
    "save automation {id}",
    "Saves an active automation permanently",
    "Automation",
)

register_command(
    "remove saved automation {id}",
    "Removes a permanently saved automation",
    "Automation",
)

register_command(
    "show saved automations",
    "Shows permanently saved automations",
    "Automation",
)

register_command(
    "show automations",
    "Shows current automations",
    "Automation",
)

register_command(
    "cancel automation {id}",
    "Cancels an automation",
    "Automation",
)

register_command(
    "clear finished automations",
    "Removes completed, cancelled, and failed automations",
    "Automation",
)

# =========================================================
# MULTI STEP COMMANDS - PHASE 4
# =========================================================

register_command(
    "{first} then {second}",
    "Runs two commands in sequence",
    "Automation",
)

register_command(
    "{first} and then {second}",
    "Runs two commands in sequence",
    "Automation",
)

# =========================================================
# APPS
# =========================================================

register_command(
    "open chrome",
    "Opens Google Chrome",
    "Apps",
    aliases=[
        "chrome kholo",
        "chrome open karo",
    ],
)

register_command(
    "open edge",
    "Opens Microsoft Edge",
    "Apps",
)

register_command(
    "open calculator",
    "Opens Calculator",
    "Apps",
    aliases=[
        "calculator kholo",
        "calculator open karo",
    ],
)

register_command(
    "open notepad",
    "Opens Notepad",
    "Apps",
)

register_command(
    "open paint",
    "Opens Paint",
    "Apps",
)

register_command(
    "open vscode",
    "Opens Visual Studio Code",
    "Apps",
    aliases=[
        "open visual studio code",
        "vs code kholo",
        "vscode kholo",
    ],
)

register_command(
    "open discord",
    "Opens Discord if installed",
    "Apps",
)

register_command(
    "close {name}",
    "Closes an application",
    "Apps",
    aliases=[
        "{name} band karo",
        "{name} close karo",
    ],
)

register_command(
    "is {name} running",
    "Checks whether an application is running",
    "Apps",
)


# =========================================================
# ADVANCED WINDOW CONTROL - PHASE 4
# =========================================================

register_command(
    "minimize current window",
    "Minimizes the currently active window",
    "Apps",
)

register_command(
    "maximize current window",
    "Maximizes the currently active window",
    "Apps",
)

register_command(
    "restore current window",
    "Restores the currently active window",
    "Apps",
)

register_command(
    "close current window",
    "Closes the currently active window",
    "Apps",
)

register_command(
    "show open windows",
    "Shows all currently open windows",
    "Apps",
)

register_command(
    "minimize {name}",
    "Minimizes an open application window",
    "Apps",
)

register_command(
    "maximize {name}",
    "Maximizes an open application window",
    "Apps",
)

register_command(
    "restore {name}",
    "Restores an open application window",
    "Apps",
)

register_command(
    "switch to {name}",
    "Switches focus to an open application window",
    "Apps",
)

register_command(
    "close window {name}",
    "Closes a specific application window",
    "Apps",
)


# =========================================================
# KEYBOARD + MOUSE CONTROL - PHASE 4
# =========================================================

register_command(
    "press {key}",
    "Presses a keyboard key or keyboard shortcut",
    "Input",
)

register_command(
    "type {text}",
    "Types text into the currently active window",
    "Input",
)

register_command(
    "click",
    "Performs a left mouse click",
    "Input",
)

register_command(
    "double click",
    "Performs a double mouse click",
    "Input",
)

register_command(
    "right click",
    "Performs a right mouse click",
    "Input",
)

register_command(
    "scroll up",
    "Scrolls upward",
    "Input",
)

register_command(
    "scroll down",
    "Scrolls downward",
    "Input",
)

register_command(
    "scroll up {amount}",
    "Scrolls upward by a selected amount",
    "Input",
)

register_command(
    "scroll down {amount}",
    "Scrolls downward by a selected amount",
    "Input",
)

register_command(
    "move mouse to {x} {y}",
    "Moves the mouse pointer to screen coordinates",
    "Input",
)

register_command(
    "click at {x} {y}",
    "Moves the mouse and clicks at screen coordinates",
    "Input",
)

register_command(
    "mouse position",
    "Shows the current mouse pointer position",
    "Input",
)


# =========================================================
# CLIPBOARD CONTROL - PHASE 4
# =========================================================

register_command(
    "copy text {text}",
    "Copies text to the clipboard",
    "Clipboard",
)

register_command(
    "show clipboard",
    "Shows the current clipboard text",
    "Clipboard",
)

register_command(
    "clear clipboard",
    "Clears the clipboard",
    "Clipboard",
)

register_command(
    "paste clipboard",
    "Pastes the current clipboard content",
    "Clipboard",
)

register_command(
    "copy selected text",
    "Copies currently selected text",
    "Clipboard",
)

register_command(
    "save clipboard to file",
    "Saves clipboard text to clipboard.txt in Documents",
    "Clipboard",
)

register_command(
    "save clipboard to {filename}",
    "Saves clipboard text to a named file in Documents",
    "Clipboard",
)



# =========================================================
# BROWSER / WEB CONTROL - PHASE 4
# =========================================================

register_command(
    "open website {website}",
    "Opens a website in the default browser",
    "Browser",
)

register_command(
    "search google for {query}",
    "Searches Google for a query",
    "Browser",
)

register_command(
    "search youtube for {query}",
    "Searches YouTube for a query",
    "Browser",
)

register_command(
    "new tab",
    "Opens a new browser tab",
    "Browser",
)

register_command(
    "close tab",
    "Closes the current browser tab",
    "Browser",
)

register_command(
    "next tab",
    "Switches to the next browser tab",
    "Browser",
)

register_command(
    "previous tab",
    "Switches to the previous browser tab",
    "Browser",
)

register_command(
    "refresh page",
    "Refreshes the current browser page",
    "Browser",
)

register_command(
    "go back",
    "Goes back in browser history",
    "Browser",
)

register_command(
    "go forward",
    "Goes forward in browser history",
    "Browser",
)

register_command(
    "focus address bar",
    "Focuses the browser address bar",
    "Browser",
)


# =========================================================
# MEDIA CONTROL - PHASE 4
# =========================================================

register_command(
    "play media",
    "Starts or toggles media playback",
    "Media",
)

register_command(
    "pause media",
    "Pauses or toggles media playback",
    "Media",
)

register_command(
    "play pause",
    "Toggles media play and pause",
    "Media",
)

register_command(
    "next track",
    "Skips to the next media track",
    "Media",
)

register_command(
    "previous track",
    "Returns to the previous media track",
    "Media",
)

register_command(
    "stop media",
    "Stops media playback",
    "Media",
)

# =========================================================
# KNOWN FOLDERS
# =========================================================

register_command(
    "open documents",
    "Opens Documents folder",
    "Files & Folders",
)

register_command(
    "open downloads",
    "Opens Downloads folder",
    "Files & Folders",
)

register_command(
    "open desktop",
    "Opens Desktop",
    "Files & Folders",
)

register_command(
    "open pictures",
    "Opens Pictures folder",
    "Files & Folders",
)

register_command(
    "open music",
    "Opens Music folder",
    "Files & Folders",
)

register_command(
    "open videos",
    "Opens Videos folder",
    "Files & Folders",
)


# =========================================================
# FULL FILE SEARCH
# =========================================================

register_command(
    "open folder {name}",
    "Searches the computer for a folder and opens it",
    "Files & Folders",
)

register_command(
    "open file {name}",
    "Searches the computer for a file and opens it",
    "Files & Folders",
)

register_command(
    "find {name}",
    "Searches the computer for a file or folder",
    "Files & Folders",
)


# =========================================================
# SPECIFIC DRIVE SEARCH
# =========================================================

register_command(
    "find {name} in {drive} drive",
    "Searches inside a selected drive",
    "Files & Folders",
)

register_command(
    "open folder {name} in {drive} drive",
    "Opens a folder from a selected drive",
    "Files & Folders",
)

register_command(
    "open file {name} in {drive} drive",
    "Opens a file from a selected drive",
    "Files & Folders",
)


# =========================================================
# DRIVE CREATE / MOVE / COPY
# =========================================================

register_command(
    "create folder {name} in {drive} drive",
    "Creates a folder in the root of a selected drive",
    "Files & Folders",
)

register_command(
    "move folder {name} to {drive} drive",
    "Moves a folder to a selected drive",
    "Files & Folders",
)

register_command(
    "move file {name} to {drive} drive",
    "Moves a file to a selected drive",
    "Files & Folders",
)

register_command(
    "copy folder {name} to {drive} drive",
    "Copies a folder to a selected drive",
    "Files & Folders",
)

register_command(
    "copy file {name} to {drive} drive",
    "Copies a file to a selected drive",
    "Files & Folders",
)


# =========================================================
# NORMAL FILE OPERATIONS
# =========================================================

register_command(
    "create folder {name}",
    "Creates a folder in Documents",
    "Files & Folders",
)

register_command(
    "create folder {name} in {location}",
    "Creates a folder in a selected location",
    "Files & Folders",
)

register_command(
    "rename folder {old} to {new}",
    "Renames a folder",
    "Files & Folders",
)

register_command(
    "rename file {old} to {new}",
    "Renames a file",
    "Files & Folders",
)

register_command(
    "move folder {name} to {location}",
    "Moves a folder",
    "Files & Folders",
)

register_command(
    "move file {name} to {location}",
    "Moves a file",
    "Files & Folders",
)

register_command(
    "copy folder {name} to {location}",
    "Copies a folder",
    "Files & Folders",
)

register_command(
    "copy file {name} to {location}",
    "Copies a file",
    "Files & Folders",
)

register_command(
    "delete folder {name}",
    "Moves a folder to Recycle Bin after confirmation",
    "Files & Folders",
)

register_command(
    "delete file {name}",
    "Moves a file to Recycle Bin after confirmation",
    "Files & Folders",
)


# =========================================================
# FILE LISTING
# =========================================================

register_command(
    "show all folders in {location}",
    "Shows all folders inside a location",
    "Files & Folders",
)

register_command(
    "show all files in {location}",
    "Shows all files inside a location",
    "Files & Folders",
)

register_command(
    "show everything in {location}",
    "Shows files and folders inside a location",
    "Files & Folders",
)

register_command(
    "show all items in {location}",
    "Shows files and folders inside a location",
    "Files & Folders",
)


# =========================================================
# DRIVE LISTING
# =========================================================

register_command(
    "show all drives",
    "Shows all accessible drives",
    "Files & Folders",
)

register_command(
    "show all folders in {drive} drive",
    "Shows folders in a selected drive",
    "Files & Folders",
)

register_command(
    "show all files in {drive} drive",
    "Shows files in a selected drive",
    "Files & Folders",
)

register_command(
    "show everything in {drive} drive",
    "Shows files and folders in a selected drive",
    "Files & Folders",
)

register_command(
    "show all items in {drive} drive",
    "Shows files and folders in a selected drive",
    "Files & Folders",
)


# =========================================================
# AUDIO
# =========================================================

register_command(
    "volume up",
    "Increases volume",
    "Audio",
)

register_command(
    "volume down",
    "Decreases volume",
    "Audio",
)

register_command(
    "set volume to {value}",
    "Sets volume to a percentage",
    "Audio",
    aliases=[
        "volume {value}",
    ],
)

register_command(
    "mute",
    "Mutes audio",
    "Audio",
)

register_command(
    "unmute",
    "Unmutes audio",
    "Audio",
)


# =========================================================
# DISPLAY
# =========================================================

register_command(
    "brightness up",
    "Increases brightness",
    "Display",
)

register_command(
    "brightness down",
    "Decreases brightness",
    "Display",
)

register_command(
    "set brightness to {value}",
    "Sets brightness to a percentage",
    "Display",
    aliases=[
        "brightness {value}",
    ],
)


# =========================================================
# CONNECTIVITY
# =========================================================

register_command(
    "wifi on",
    "Turns Wi-Fi on",
    "Connectivity",
    aliases=[
        "wifi chalu karo",
        "wifi on karo",
    ],
)

register_command(
    "wifi off",
    "Turns Wi-Fi off",
    "Connectivity",
    aliases=[
        "wifi band karo",
        "wifi off karo",
    ],
)

register_command(
    "bluetooth on",
    "Turns Bluetooth on",
    "Connectivity",
    aliases=[
        "bluetooth chalu karo",
        "bluetooth on karo",
    ],
)

register_command(
    "bluetooth off",
    "Turns Bluetooth off",
    "Connectivity",
    aliases=[
        "bluetooth band karo",
        "bluetooth off karo",
    ],
)



# =========================================================
# SCREENSHOT / SCREEN CONTROL - PHASE 4
# =========================================================

register_command(
    "take screenshot",
    "Takes a screenshot and saves it in WizzArc Screenshots",
    "Screen",
)

register_command(
    "take screenshot of screen",
    "Takes a screenshot of the screen",
    "Screen",
)

register_command(
    "save screenshot as {name}",
    "Takes a screenshot with a custom file name",
    "Screen",
)

register_command(
    "open screenshots folder",
    "Opens the WizzArc Screenshots folder",
    "Screen",
)

register_command(
    "show screen size",
    "Shows the current screen resolution",
    "Screen",
)

register_command(
    "show mouse position",
    "Shows the current mouse pointer position",
    "Screen",
)

# =========================================================
# QUICK ACTIONS
# =========================================================

register_command(
    "take screenshot",
    "Takes a screenshot",
    "Quick Actions",
)

register_command(
    "lock computer",
    "Locks the PC",
    "Quick Actions",
)

register_command(
    "shutdown",
    "Shows shutdown confirmation",
    "Quick Actions",
)

register_command(
    "restart",
    "Shows restart confirmation",
    "Quick Actions",
)

# =========================================================
# SCREEN VISION / OCR - PHASE 6
# =========================================================

register_command(
    "read screen",
    "Reads visible text from the current screen using OCR",
    "Screen Vision",
)

register_command(
    "read text on screen",
    "Reads visible text from the current screen using OCR",
    "Screen Vision",
)

register_command(
    "find text {text} on screen",
    "Finds visible text on screen and returns its coordinates",
    "Screen Vision",
)

register_command(
    "read region {x} {y} {width} {height}",
    "Reads visible text from a selected screen region",
    "Screen Vision",
)


register_command(
    "click text {text}",
    "Finds visible text on screen and clicks the first match",
    "Screen Vision",
)






register_command(
    "what can you see",
    "Summarizes visible text and screen elements",
    "Screen Vision",
)

register_command(
    "what is on my screen",
    "Summarizes visible text and screen elements",
    "Screen Vision",
)

register_command(
    "show visible elements",
    "Lists detected visible screen elements and coordinates",
    "Screen Vision",
)


register_command(
    "show clickable elements",
    "Lists likely clickable visible text elements and coordinates",
    "Screen Vision",
)


register_command(
    "refresh screen snapshot",
    "Rescans the screen and caches stable clickable element numbering",
    "Screen Vision",
)

register_command(
    "clear screen snapshot",
    "Clears the cached screen element snapshot",
    "Screen Vision",
)


register_command(
    "screen snapshot status",
    "Shows whether the cached screen snapshot is fresh or expired",
    "Screen Vision",
)


register_command(
    "screen change status",
    "Checks whether the screen changed after the cached snapshot",
    "Screen Vision",
)


register_command(
    "show screen context",
    "Groups visible screen elements by screen region",
    "Screen Vision",
)

register_command(
    "context around {text}",
    "Shows nearby visible text around a selected screen element",
    "Screen Vision",
)

register_command(
    "show cached clickable elements",
    "Shows clickable elements from the current cached screen snapshot",
    "Screen Vision",
)


register_command(
    "click element {number}",
    "Clicks a numbered likely-clickable screen element",
    "Screen Vision",
)

register_command(
    "move to element {number}",
    "Moves the mouse to a numbered likely-clickable screen element",
    "Screen Vision",
)

register_command(
    "double click element {number}",
    "Double clicks a numbered likely-clickable screen element",
    "Screen Vision",
)

register_command(
    "right click element {number}",
    "Right clicks a numbered likely-clickable screen element",
    "Screen Vision",
)

register_command(
    "is {text} visible",
    "Checks whether selected text is visible on screen",
    "Screen Vision",
)

register_command(
    "where is {text}",
    "Shows the coordinates of matching visible text",
    "Screen Vision",
)

register_command(
    "find and click text {text}",
    "Finds visible text on screen and clicks the first match",
    "Screen Vision",
)

register_command(
    "find and double click text {text}",
    "Finds visible text on screen and double clicks the first match",
    "Screen Vision",
)

register_command(
    "find and right click text {text}",
    "Finds visible text on screen and right clicks the first match",
    "Screen Vision",
)

register_command(
    "move to text {text}",
    "Moves the mouse pointer to the first matching visible text",
    "Screen Vision",
)

register_command(
    "double click text {text}",
    "Double clicks the first matching visible text",
    "Screen Vision",
)

register_command(
    "right click text {text}",
    "Right clicks the first matching visible text",
    "Screen Vision",
)


register_command(
    "click first text {text}",
    "Clicks the first matching visible text on screen",
    "Screen Vision",
)

register_command(
    "click second text {text}",
    "Clicks the second matching visible text on screen",
    "Screen Vision",
)

register_command(
    "click third text {text}",
    "Clicks the third matching visible text on screen",
    "Screen Vision",
)

register_command(
    "click last text {text}",
    "Clicks the last matching visible text on screen",
    "Screen Vision",
)

register_command(
    "click {number} text {text}",
    "Clicks a numbered matching visible text on screen",
    "Screen Vision",
)
