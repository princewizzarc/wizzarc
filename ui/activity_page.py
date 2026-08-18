from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.activity_logger import (
    ACTIVITY_LOG_PATH,
    clear_activity,
    read_activity,
)
from core.crash_logger import (
    ERROR_LOG_PATH,
)


class ActivityPage(QWidget):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.setObjectName(
            "activityPage"
        )

        self._build_ui()
        self.refresh()

    def _build_ui(
        self,
    ):
        root = QVBoxLayout(self)
        root.setContentsMargins(
            30,
            26,
            30,
            26,
        )
        root.setSpacing(14)

        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title = QLabel(
            "Activity"
        )
        title.setObjectName(
            "activityTitle"
        )

        subtitle = QLabel(
            "Recent commands, AI activity, system actions, and errors."
        )
        subtitle.setObjectName(
            "activitySubtitle"
        )

        title_box.addWidget(
            title
        )
        title_box.addWidget(
            subtitle
        )

        header.addLayout(
            title_box
        )
        header.addStretch()

        self.refresh_button = QPushButton(
            "Refresh"
        )
        self.refresh_button.setObjectName(
            "activityButton"
        )

        self.clear_button = QPushButton(
            "Clear Activity"
        )
        self.clear_button.setObjectName(
            "activityDangerButton"
        )

        header.addWidget(
            self.refresh_button
        )
        header.addWidget(
            self.clear_button
        )

        root.addLayout(
            header
        )

        path_note = QLabel(
            f"Activity log: {ACTIVITY_LOG_PATH}\n"
            f"Error log: {ERROR_LOG_PATH}"
        )
        path_note.setWordWrap(
            True
        )
        path_note.setObjectName(
            "activityPath"
        )
        root.addWidget(
            path_note
        )

        self.summary_label = QLabel(
            ""
        )
        self.summary_label.setObjectName(
            "activitySummary"
        )
        root.addWidget(
            self.summary_label
        )

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(
            True
        )
        self.scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.content = QWidget()
        self.content_layout = QVBoxLayout(
            self.content
        )
        self.content_layout.setContentsMargins(
            0,
            0,
            8,
            0,
        )
        self.content_layout.setSpacing(
            10
        )
        self.content_layout.addStretch()

        self.scroll.setWidget(
            self.content
        )

        root.addWidget(
            self.scroll,
            1,
        )

        self.refresh_button.clicked.connect(
            self.refresh
        )
        self.clear_button.clicked.connect(
            self.clear_log
        )

        self.setStyleSheet(
            """
            #activityPage {
                background: #05070b;
            }

            #activityTitle {
                color: #f4f8ff;
                font-size: 26px;
                font-weight: 700;
            }

            #activitySubtitle,
            #activityPath {
                color: #748198;
                font-size: 12px;
            }

            #activitySummary {
                color: #aebbd0;
                font-size: 12px;
            }

            #activityCard {
                background: #0b1018;
                border: 1px solid #1b2738;
                border-radius: 12px;
            }

            #activityTime {
                color: #6f7f97;
                font-size: 11px;
            }

            #activityType {
                color: #b9c7dc;
                font-size: 11px;
                font-weight: 650;
            }

            #activityMessage {
                color: #eef4ff;
                font-size: 13px;
            }

            #activitySource {
                color: #718198;
                font-size: 11px;
            }

            #activityButton,
            #activityDangerButton {
                border-radius: 8px;
                padding: 8px 13px;
                font-weight: 600;
            }

            #activityButton {
                background: #101824;
                color: #d8e2f0;
                border: 1px solid #29384e;
            }

            #activityButton:hover {
                background: #172234;
            }

            #activityDangerButton {
                background: #241318;
                color: #f2c4cc;
                border: 1px solid #54303a;
            }

            #activityDangerButton:hover {
                background: #321a21;
            }

            QScrollArea {
                background: transparent;
                border: none;
            }
            """
        )

    def _clear_cards(
        self,
    ):
        while (
            self.content_layout.count()
            > 1
        ):
            item = (
                self.content_layout.takeAt(
                    0
                )
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def _make_card(
        self,
        entry,
    ):
        card = QFrame()
        card.setObjectName(
            "activityCard"
        )

        layout = QVBoxLayout(
            card
        )
        layout.setContentsMargins(
            14,
            11,
            14,
            11,
        )
        layout.setSpacing(
            4
        )

        top = QHBoxLayout()

        event_type = QLabel(
            str(
                entry.get(
                    "type",
                    "activity",
                )
            ).replace(
                "_",
                " ",
            ).title()
        )
        event_type.setObjectName(
            "activityType"
        )

        timestamp = QLabel(
            str(
                entry.get(
                    "time",
                    "",
                )
            )
        )
        timestamp.setObjectName(
            "activityTime"
        )

        top.addWidget(
            event_type
        )
        top.addStretch()
        top.addWidget(
            timestamp
        )

        message = QLabel(
            str(
                entry.get(
                    "message",
                    "",
                )
            )
        )
        message.setWordWrap(
            True
        )
        message.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        message.setObjectName(
            "activityMessage"
        )

        source = QLabel(
            f"Source: "
            f"{entry.get('source', 'WizzArc')}  •  "
            f"Status: {entry.get('status', 'info')}"
        )
        source.setObjectName(
            "activitySource"
        )

        layout.addLayout(
            top
        )
        layout.addWidget(
            message
        )
        layout.addWidget(
            source
        )

        return card

    def refresh(
        self,
    ):
        self._clear_cards()

        entries = read_activity(
            limit=250
        )

        error_exists = (
            ERROR_LOG_PATH.exists()
            and ERROR_LOG_PATH.stat().st_size > 0
        )

        self.summary_label.setText(
            f"{len(entries)} recent activity entries"
            + (
                "  •  Error log has entries"
                if error_exists
                else "  •  No recorded errors"
            )
        )

        if not entries:
            empty = QLabel(
                "No activity recorded yet."
            )
            empty.setObjectName(
                "activitySubtitle"
            )
            self.content_layout.insertWidget(
                0,
                empty,
            )
            return

        for entry in entries:
            self.content_layout.insertWidget(
                self.content_layout.count() - 1,
                self._make_card(
                    entry
                ),
            )

    def clear_log(
        self,
    ):
        answer = QMessageBox.question(
            self,
            "Clear Activity",
            "Clear WizzArc activity history? "
            "The separate error log will not be deleted.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        if clear_activity():
            self.refresh()