from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QFrame,
)

from brain.custom_app_manager import CUSTOM_APP_MANAGER


class CustomAppsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_app_id = None

        self.setObjectName("CustomAppsPage")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Custom App & Command Manager")
        title.setStyleSheet(
            "font-size: 24px; font-weight: 700;"
        )
        root.addWidget(title)

        subtitle = QLabel(
            "Add apps once, then open them using your own WizzArc commands."
        )
        subtitle.setStyleSheet(
            "color: #a9a9c7; font-size: 13px;"
        )
        root.addWidget(subtitle)

        content = QHBoxLayout()
        content.setSpacing(18)
        root.addLayout(content)

        # =================================================
        # LEFT - SAVED APPS
        # =================================================

        left = QFrame()
        left.setObjectName("CustomAppsListPanel")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(10)

        saved_label = QLabel("Saved Apps")
        saved_label.setStyleSheet(
            "font-size: 16px; font-weight: 600;"
        )
        left_layout.addWidget(saved_label)

        self.apps_list = QListWidget()
        self.apps_list.itemSelectionChanged.connect(
            self.load_selected_app
        )
        left_layout.addWidget(self.apps_list)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(
            self.refresh_apps
        )
        left_layout.addWidget(refresh_btn)

        content.addWidget(left, 1)

        # =================================================
        # RIGHT - FORM
        # =================================================

        right = QFrame()
        right.setObjectName("CustomAppsFormPanel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(18, 18, 18, 18)
        right_layout.setSpacing(12)

        form_title = QLabel("App Details")
        form_title.setStyleSheet(
            "font-size: 16px; font-weight: 600;"
        )
        right_layout.addWidget(form_title)

        right_layout.addWidget(
            QLabel("App Name")
        )

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "Example: PyCharm"
        )
        self.name_input.textChanged.connect(
            self.auto_fill_command
        )
        right_layout.addWidget(
            self.name_input
        )

        right_layout.addWidget(
            QLabel("Executable Path")
        )

        path_row = QHBoxLayout()

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(
            r"C:\Program Files\...\app.exe"
        )
        path_row.addWidget(
            self.path_input,
            1,
        )

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(
            self.browse_executable
        )
        path_row.addWidget(
            browse_btn
        )

        right_layout.addLayout(
            path_row
        )

        right_layout.addWidget(
            QLabel("Main Command")
        )

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText(
            "Example: open pycharm"
        )
        right_layout.addWidget(
            self.command_input
        )

        right_layout.addWidget(
            QLabel("Aliases")
        )

        self.aliases_input = QLineEdit()
        self.aliases_input.setPlaceholderText(
            "Comma separated: launch pycharm, start pycharm"
        )
        right_layout.addWidget(
            self.aliases_input
        )

        self.enabled_check = QCheckBox(
            "Enabled"
        )
        self.enabled_check.setChecked(
            True
        )
        right_layout.addWidget(
            self.enabled_check
        )

        action_row_1 = QHBoxLayout()

        add_btn = QPushButton(
            "Add New"
        )
        add_btn.clicked.connect(
            self.add_app
        )
        action_row_1.addWidget(
            add_btn
        )

        update_btn = QPushButton(
            "Update Selected"
        )
        update_btn.clicked.connect(
            self.update_app
        )
        action_row_1.addWidget(
            update_btn
        )

        right_layout.addLayout(
            action_row_1
        )

        action_row_2 = QHBoxLayout()

        clear_btn = QPushButton(
            "Clear Form"
        )
        clear_btn.clicked.connect(
            self.clear_form
        )
        action_row_2.addWidget(
            clear_btn
        )

        delete_btn = QPushButton(
            "Delete Selected"
        )
        delete_btn.clicked.connect(
            self.delete_selected_app
        )
        action_row_2.addWidget(
            delete_btn
        )

        right_layout.addLayout(
            action_row_2
        )

        self.status_label = QLabel(
            ""
        )
        self.status_label.setWordWrap(
            True
        )
        self.status_label.setStyleSheet(
            "color: #9da7ff;"
        )
        right_layout.addWidget(
            self.status_label
        )

        right_layout.addStretch()

        content.addWidget(
            right,
            2,
        )

        self.apply_styles()
        self.refresh_apps()

    # =====================================================
    # STYLE
    # =====================================================

    def apply_styles(self):

        self.setStyleSheet(
            """
            QWidget#CustomAppsPage {
                background: #090a12;
                color: #f0f0ff;
            }

            QFrame#CustomAppsListPanel,
            QFrame#CustomAppsFormPanel {
                background: #0f1120;
                border: 1px solid #292d4d;
                border-radius: 14px;
            }

            QLineEdit, QListWidget {
                background: #0a0c16;
                border: 1px solid #30355b;
                border-radius: 8px;
                padding: 9px;
                color: #f3f3ff;
            }

            QLineEdit:focus, QListWidget:focus {
                border: 1px solid #6f63ff;
            }

            QPushButton {
                background: #171a2d;
                border: 1px solid #3b416e;
                border-radius: 8px;
                padding: 9px 14px;
                color: #f4f4ff;
            }

            QPushButton:hover {
                background: #232844;
            }

            QPushButton:pressed {
                background: #111423;
            }

            QCheckBox {
                spacing: 8px;
            }
            """
        )

    # =====================================================
    # HELPERS
    # =====================================================

    def parse_aliases(
        self,
    ):

        raw = self.aliases_input.text()

        return [
            item.strip()
            for item in raw.split(",")
            if item.strip()
        ]

    def auto_fill_command(
        self,
        name,
    ):

        # Only auto-fill for a fresh form.
        if self.current_app_id is not None:
            return

        if not self.command_input.text().strip():
            cleaned = (
                str(name)
                .lower()
                .strip()
            )

            if cleaned:
                self.command_input.setText(
                    f"open {cleaned}"
                )

    def browse_executable(
        self,
    ):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application",
            "",
            "Applications (*.exe *.bat *.cmd *.com);;All Files (*.*)",
        )

        if not path:
            return

        self.path_input.setText(
            path
        )

        if not self.name_input.text().strip():

            guessed_name = (
                Path(path)
                .stem
                .replace("64", "")
                .replace("_", " ")
                .strip()
            )

            self.name_input.setText(
                guessed_name
            )

    def refresh_apps(
        self,
    ):

        self.apps_list.clear()

        apps = (
            CUSTOM_APP_MANAGER
            .list_apps()
        )

        for app in apps:

            state = (
                "ON"
                if app.enabled
                else "OFF"
            )

            item = QListWidgetItem(
                f"{app.name}  [{state}]\n{app.command}"
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                app.id,
            )

            self.apps_list.addItem(
                item
            )

        self.status_label.setText(
            f"{len(apps)} custom app(s) saved."
        )

    def load_selected_app(
        self,
    ):

        items = (
            self.apps_list
            .selectedItems()
        )

        if not items:
            return

        app_id = items[0].data(
            Qt.ItemDataRole.UserRole
        )

        app = (
            CUSTOM_APP_MANAGER
            .get_app(
                app_id
            )
        )

        if app is None:
            return

        self.current_app_id = app.id

        self.name_input.setText(
            app.name
        )

        self.path_input.setText(
            app.executable_path
        )

        self.command_input.setText(
            app.command
        )

        self.aliases_input.setText(
            ", ".join(
                app.aliases
            )
        )

        self.enabled_check.setChecked(
            app.enabled
        )

        self.status_label.setText(
            f"Editing: {app.name}"
        )

    def clear_form(
        self,
    ):

        self.current_app_id = None

        self.name_input.clear()
        self.path_input.clear()
        self.command_input.clear()
        self.aliases_input.clear()

        self.enabled_check.setChecked(
            True
        )

        self.apps_list.clearSelection()

        self.status_label.setText(
            "Ready to add a new app."
        )

    # =====================================================
    # ACTIONS
    # =====================================================

    def add_app(
        self,
    ):

        try:

            app = (
                CUSTOM_APP_MANAGER
                .add_app(
                    name=self.name_input.text(),
                    executable_path=self.path_input.text(),
                    command=self.command_input.text(),
                    aliases=self.parse_aliases(),
                    enabled=self.enabled_check.isChecked(),
                )
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "Could not add app",
                str(error),
            )
            return

        self.status_label.setText(
            f"Added {app.name}."
        )

        self.clear_form()
        self.refresh_apps()

    def update_app(
        self,
    ):

        if not self.current_app_id:

            QMessageBox.information(
                self,
                "Select an app",
                "Select a saved app first.",
            )
            return

        try:

            app = (
                CUSTOM_APP_MANAGER
                .update_app(
                    self.current_app_id,
                    name=self.name_input.text(),
                    executable_path=self.path_input.text(),
                    command=self.command_input.text(),
                    aliases=self.parse_aliases(),
                    enabled=self.enabled_check.isChecked(),
                )
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "Could not update app",
                str(error),
            )
            return

        self.status_label.setText(
            f"Updated {app.name}."
        )

        self.refresh_apps()

    def delete_selected_app(
        self,
    ):

        if not self.current_app_id:

            QMessageBox.information(
                self,
                "Select an app",
                "Select a saved app first.",
            )
            return

        app = (
            CUSTOM_APP_MANAGER
            .get_app(
                self.current_app_id
            )
        )

        if app is None:
            return

        confirm = QMessageBox.question(
            self,
            "Delete custom app",
            f"Delete '{app.name}' from WizzArc?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        removed = (
            CUSTOM_APP_MANAGER
            .delete_app(
                self.current_app_id
            )
        )

        if removed:
            self.clear_form()
            self.refresh_apps()
            self.status_label.setText(
                f"Deleted {app.name}."
            )