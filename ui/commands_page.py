from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QFrame,
)

from brain.command_registry import get_commands_by_category
from brain.custom_app_manager import CUSTOM_APP_MANAGER


class CommandsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("page")
        self._rows = []

        root = QVBoxLayout(self)
        root.setContentsMargins(35, 25, 35, 30)
        root.setSpacing(14)

        title = QLabel("Commands Guide")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        description = QLabel(
            "Browse built-in WizzArc commands and your custom app commands."
        )
        description.setObjectName("pageDescription")
        root.addWidget(description)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("commandGuideSearch")
        self.search_input.setPlaceholderText(
            "Search commands, aliases, apps or actions..."
        )
        self.search_input.textChanged.connect(
            self.apply_filter
        )
        root.addWidget(self.search_input)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(14)
        self.container_layout.addStretch()

        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll, 1)

        self.refresh_commands()

    # =====================================================
    # PAGE REFRESH
    # =====================================================

    def showEvent(self, event):
        # Important for Improvement #8:
        # when user adds/edits/deletes an app, reopening
        # Commands Guide immediately reflects the JSON data.
        self.refresh_commands()

        # Always start the guide from the top. Without this,
        # QScrollArea can remember an older scroll position and
        # the first "Custom Apps" card may sit just above the
        # visible viewport, making Automation look like section #1.
        QTimer.singleShot(
            0,
            self.scroll_to_top,
        )

        super().showEvent(event)

    def clear_cards(self):

        while self.container_layout.count():

            item = self.container_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self._rows = []

    # =====================================================
    # DATA
    # =====================================================

    def get_guide_categories(self):

        categories = {}

        # Existing built-in registry commands.
        for category, definitions in (
            get_commands_by_category().items()
        ):
            categories[category] = []

            for definition in definitions:

                categories[category].append(
                    {
                        "command": definition.command,
                        "description": definition.description,
                        "aliases": list(
                            getattr(
                                definition,
                                "aliases",
                                (),
                            )
                        ),
                        "custom": False,
                        "enabled": True,
                    }
                )

        # Improvement #8 custom app commands.
        custom_entries = []

        for app in CUSTOM_APP_MANAGER.list_apps():

            state = (
                "Enabled"
                if app.enabled
                else "Disabled"
            )

            custom_entries.append(
                {
                    "command": app.command,
                    "description": (
                        f"Opens custom app: {app.name} "
                        f"({state})"
                    ),
                    "aliases": list(app.aliases),
                    "custom": True,
                    "enabled": app.enabled,
                }
            )

        if custom_entries:
            # Improvement #8:
            # Custom Apps should always appear FIRST in the guide
            # so newly added commands are immediately visible.
            ordered_categories = {
                "Custom Apps": custom_entries
            }

            for category, entries in categories.items():
                ordered_categories[category] = entries

            return ordered_categories

        return categories

    # =====================================================
    # UI BUILD
    # =====================================================

    def refresh_commands(self):

        current_search = self.search_input.text()

        self.clear_cards()

        categories = self.get_guide_categories()

        for category, commands in categories.items():

            card = QFrame()
            card.setObjectName("commandGuideCard")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(
                14,
                12,
                14,
                14,
            )
            card_layout.setSpacing(8)

            heading = QLabel(category)
            heading.setObjectName("commandGuideTitle")
            card_layout.addWidget(heading)

            category_rows = []

            for entry in commands:

                # Main command row.
                row = self.create_command_row(
                    command=entry["command"],
                    description=entry["description"],
                    search_extra=(
                        " ".join(entry["aliases"])
                        + " "
                        + category
                        + (
                            " custom app"
                            if entry["custom"]
                            else ""
                        )
                    ),
                    is_alias=False,
                    enabled=entry["enabled"],
                )

                card_layout.addWidget(row)
                category_rows.append(row)

                # Show aliases in guide too so user knows
                # every phrase they can actually type.
                for alias in entry["aliases"]:

                    alias_row = self.create_command_row(
                        command=alias,
                        description=(
                            f"Alias for: {entry['command']}"
                        ),
                        search_extra=(
                            entry["command"]
                            + " "
                            + entry["description"]
                            + " "
                            + category
                        ),
                        is_alias=True,
                        enabled=entry["enabled"],
                    )

                    card_layout.addWidget(alias_row)
                    category_rows.append(alias_row)

            self.container_layout.addWidget(card)

            self._rows.append(
                {
                    "card": card,
                    "heading": heading,
                    "category": category,
                    "rows": category_rows,
                }
            )

        self.container_layout.addStretch()

        self.search_input.setText(
            current_search
        )
        self.apply_filter(
            current_search
        )

        QTimer.singleShot(
            0,
            self.scroll_to_top,
        )

    def create_command_row(
        self,
        *,
        command,
        description,
        search_extra="",
        is_alias=False,
        enabled=True,
    ):

        row = QFrame()
        row.setObjectName("commandGuideRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(
            12,
            8,
            12,
            8,
        )
        layout.setSpacing(14)

        command_text = str(command).strip()

        command_label = QLabel(
            (
                "↳ " + command_text
                if is_alias
                else command_text
            )
        )
        command_label.setObjectName(
            "commandGuideCommand"
        )
        command_label.setMinimumWidth(280)

        action_label = QLabel(description)
        action_label.setObjectName(
            "commandGuideAction"
        )
        action_label.setWordWrap(True)

        layout.addWidget(command_label)
        layout.addWidget(action_label, 1)

        row._guide_search_text = (
            f"{command_text} "
            f"{description} "
            f"{search_extra}"
        ).lower()

        row._guide_enabled = enabled

        if not enabled:
            row.setToolTip(
                "This custom command is currently disabled."
            )

        return row

    def scroll_to_top(self):

        bar = self.scroll.verticalScrollBar()

        if bar is not None:
            bar.setValue(
                bar.minimum()
            )

    # =====================================================
    # FILTER
    # =====================================================

    def apply_filter(self, text):

        query = (
            str(text)
            .lower()
            .strip()
        )

        for category_info in self._rows:

            visible_count = 0

            for row in category_info["rows"]:

                visible = (
                    not query
                    or query
                    in row._guide_search_text
                )

                row.setVisible(visible)

                if visible:
                    visible_count += 1

            # Category heading/card disappears if no matching
            # command exists inside it.
            category_info["card"].setVisible(
                visible_count > 0
            )