from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class FilesPage(QFrame):

    def __init__(self):
        super().__init__()

        self.setObjectName("page")

        self.current_items = []

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            45,
            35,
            45,
            35
        )

        main_layout.setSpacing(
            15
        )

        # =================================================
        # TITLE
        # =================================================

        title_row = QHBoxLayout()

        title_box = QVBoxLayout()

        title = QLabel(
            "Files"
        )

        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "Browse files and folders found by WizzArc."
        )

        description.setObjectName(
            "pageDescription"
        )

        title_box.addWidget(
            title
        )

        title_box.addWidget(
            description
        )

        title_row.addLayout(
            title_box
        )

        title_row.addStretch()

        self.location_label = QLabel(
            "Location: —"
        )

        self.location_label.setObjectName(
            "filesLocation"
        )

        title_row.addWidget(
            self.location_label
        )

        main_layout.addLayout(
            title_row
        )

        # =================================================
        # SEARCH BAR
        # =================================================

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Filter shown files and folders..."
        )

        self.search_input.setObjectName(
            "filesSearch"
        )

        self.search_input.textChanged.connect(
            self.filter_items
        )

        main_layout.addWidget(
            self.search_input
        )

        # =================================================
        # INFO BAR
        # =================================================

        info_row = QHBoxLayout()

        self.count_label = QLabel(
            "0 items"
        )

        self.count_label.setObjectName(
            "filesCount"
        )

        info_row.addWidget(
            self.count_label
        )

        info_row.addStretch()

        self.clear_button = QPushButton(
            "Clear"
        )

        self.clear_button.setObjectName(
            "filesClearButton"
        )

        self.clear_button.clicked.connect(
            self.clear_results
        )

        info_row.addWidget(
            self.clear_button
        )

        main_layout.addLayout(
            info_row
        )

        # =================================================
        # SCROLL AREA
        # =================================================

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.results_widget = QWidget()

        self.results_layout = QVBoxLayout(
            self.results_widget
        )

        self.results_layout.setContentsMargins(
            0,
            5,
            5,
            5
        )

        self.results_layout.setSpacing(
            10
        )

        self.empty_label = QLabel(
            "No file or folder results yet."
        )

        self.empty_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.empty_label.setObjectName(
            "filesEmpty"
        )

        self.results_layout.addWidget(
            self.empty_label
        )

        self.results_layout.addStretch()

        self.scroll_area.setWidget(
            self.results_widget
        )

        main_layout.addWidget(
            self.scroll_area,
            1
        )

    # =====================================================
    # SHOW ITEMS
    # =====================================================

    def show_items(
        self,
        location,
        items
    ):

        self.clear_result_rows()

        self.location_label.setText(
            f"Location: {location.title()}"
        )

        self.current_items = []

        for item in items:

            try:

                item_type = (
                    "Folder"
                    if item.is_dir()
                    else "File"
                )

                item_data = {
                    "name": item.name,
                    "path": str(item),
                    "type": item_type,
                    "object": item,
                }

                self.current_items.append(
                    item_data
                )

                row = self.create_item_row(
                    item_data
                )

                self.results_layout.insertWidget(
                    self.results_layout.count() - 1,
                    row
                )

            except Exception:
                continue

        count = len(
            self.current_items
        )

        self.count_label.setText(
            f"{count} item"
            + (
                ""
                if count == 1
                else "s"
            )
        )

        self.empty_label.setVisible(
            count == 0
        )

    # =====================================================
    # CREATE ROW
    # =====================================================

    def create_item_row(
        self,
        item_data
    ):

        row = QFrame()

        row.setObjectName(
            "filesItemRow"
        )

        row.setProperty(
            "searchText",
            (
                f"{item_data['name']} "
                f"{item_data['type']} "
                f"{item_data['path']}"
            ).lower()
        )

        row_layout = QHBoxLayout(
            row
        )

        row_layout.setContentsMargins(
            15,
            12,
            15,
            12
        )

        row_layout.setSpacing(
            15
        )

        # =================================================
        # TYPE ICON
        # =================================================

        icon_text = (
            "📁"
            if item_data["type"] == "Folder"
            else "📄"
        )

        icon_label = QLabel(
            icon_text
        )

        icon_label.setObjectName(
            "filesItemIcon"
        )

        icon_label.setFixedWidth(
            30
        )

        row_layout.addWidget(
            icon_label
        )

        # =================================================
        # NAME + PATH
        # =================================================

        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            3
        )

        name_label = QLabel(
            item_data["name"]
        )

        name_label.setObjectName(
            "filesItemName"
        )

        path_label = QLabel(
            item_data["path"]
        )

        path_label.setObjectName(
            "filesItemPath"
        )

        path_label.setWordWrap(
            True
        )

        text_layout.addWidget(
            name_label
        )

        text_layout.addWidget(
            path_label
        )

        row_layout.addLayout(
            text_layout,
            1
        )

        # =================================================
        # TYPE LABEL
        # =================================================

        type_label = QLabel(
            item_data["type"]
        )

        type_label.setObjectName(
            "filesItemType"
        )

        row_layout.addWidget(
            type_label
        )

        # =================================================
        # OPEN BUTTON
        # =================================================

        open_button = QPushButton(
            "Open"
        )

        open_button.setObjectName(
            "filesOpenButton"
        )

        open_button.clicked.connect(
            lambda checked=False, obj=item_data["object"]:
            self.open_item(obj)
        )

        row_layout.addWidget(
            open_button
        )

        return row

    # =====================================================
    # OPEN ITEM
    # =====================================================

    def open_item(
        self,
        item
    ):

        try:

            import os

            os.startfile(
                str(item)
            )

        except Exception as error:

            self.location_label.setText(
                f"Couldn't open item: {error}"
            )

    # =====================================================
    # FILTER
    # =====================================================

    def filter_items(
        self,
        text
    ):

        query = (
            text
            .lower()
            .strip()
        )

        for index in range(
            self.results_layout.count()
        ):

            widget = (
                self.results_layout
                .itemAt(index)
                .widget()
            )

            if widget is None:
                continue

            if widget is self.empty_label:
                continue

            search_text = widget.property(
                "searchText"
            )

            if search_text is None:
                continue

            visible = (
                not query
                or query in search_text
            )

            widget.setVisible(
                visible
            )

    # =====================================================
    # CLEAR ROWS
    # =====================================================

    def clear_result_rows(self):

        for index in reversed(
            range(
                self.results_layout.count()
            )
        ):

            item = (
                self.results_layout
                .itemAt(index)
            )

            widget = item.widget()

            if (
                widget is not None
                and widget is not self.empty_label
            ):

                self.results_layout.removeWidget(
                    widget
                )

                widget.deleteLater()

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(self):

        self.clear_result_rows()

        self.current_items = []

        self.location_label.setText(
            "Location: —"
        )

        self.count_label.setText(
            "0 items"
        )

        self.empty_label.show()

        self.search_input.clear()