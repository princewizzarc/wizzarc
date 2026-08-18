from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.settings_manager import (
    DEFAULT_SETTINGS,
    SETTINGS_MANAGER,
)


class SettingsPage(QWidget):

    settings_saved = Signal(dict)

    def __init__(
        self,
        settings_manager=None,
        parent=None,
    ):
        super().__init__(parent)

        self.settings_manager = (
            settings_manager
            or SETTINGS_MANAGER
        )

        self.setObjectName(
            "settingsPage"
        )

        self._build_ui()
        self.load_settings()

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(
        self,
    ):
        root = QVBoxLayout(self)
        root.setContentsMargins(
            34,
            28,
            34,
            28,
        )
        root.setSpacing(18)

        title = QLabel(
            "Settings"
        )
        title.setObjectName(
            "settingsTitle"
        )

        subtitle = QLabel(
            "Customize WizzArc behavior and startup preferences."
        )
        subtitle.setObjectName(
            "settingsSubtitle"
        )

        root.addWidget(title)
        root.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        content = QWidget()
        content.setObjectName(
            "settingsContent"
        )

        content_layout = QVBoxLayout(
            content
        )
        content_layout.setContentsMargins(
            0,
            4,
            8,
            4,
        )
        content_layout.setSpacing(14)

        # ---------------------------------------------
        # Voice / Wake
        # ---------------------------------------------

        voice_card = self._make_card(
            "Voice & Wake"
        )

        self.wake_phrase_input = QLineEdit()
        self.wake_phrase_input.setPlaceholderText(
            "wizzarc"
        )

        voice_card.layout().addWidget(
            self._field_label(
                "Wake phrase"
            )
        )
        voice_card.layout().addWidget(
            self.wake_phrase_input
        )

        self.speech_checkbox = QCheckBox(
            "Speak WizzArc replies aloud"
        )
        voice_card.layout().addWidget(
            self.speech_checkbox
        )

        self.mic_default_checkbox = QCheckBox(
            "Start with Always-On Mic enabled"
        )
        voice_card.layout().addWidget(
            self.mic_default_checkbox
        )

        mic_note = QLabel(
            "Always-On Mic default is applied the next time WizzArc starts."
        )
        mic_note.setWordWrap(True)
        mic_note.setObjectName(
            "settingsNote"
        )
        voice_card.layout().addWidget(
            mic_note
        )

        content_layout.addWidget(
            voice_card
        )

        # ---------------------------------------------
        # AI
        # ---------------------------------------------

        ai_card = self._make_card(
            "AI"
        )

        ai_card.layout().addWidget(
            self._field_label(
                "Local Ollama model"
            )
        )

        self.ai_model_combo = QComboBox()
        self.ai_model_combo.setEditable(
            True
        )
        self.ai_model_combo.addItems(
            [
                "qwen3:4b",
            ]
        )

        ai_card.layout().addWidget(
            self.ai_model_combo
        )

        model_note = QLabel(
            "The selected model must already exist in Ollama. "
            "Changing it reconnects WizzArc's AI backend."
        )
        model_note.setWordWrap(True)
        model_note.setObjectName(
            "settingsNote"
        )
        ai_card.layout().addWidget(
            model_note
        )

        content_layout.addWidget(
            ai_card
        )

        # ---------------------------------------------
        # Startup
        # ---------------------------------------------

        startup_card = self._make_card(
            "Startup"
        )

        self.start_minimized_checkbox = QCheckBox(
            "Start WizzArc minimized"
        )

        startup_card.layout().addWidget(
            self.start_minimized_checkbox
        )

        startup_note = QLabel(
            "This preference takes effect on the next launch."
        )
        startup_note.setWordWrap(True)
        startup_note.setObjectName(
            "settingsNote"
        )
        startup_card.layout().addWidget(
            startup_note
        )

        content_layout.addWidget(
            startup_card
        )
        content_layout.addStretch()

        scroll.setWidget(
            content
        )
        root.addWidget(
            scroll,
            1,
        )

        # ---------------------------------------------
        # Actions
        # ---------------------------------------------

        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.reset_button = QPushButton(
            "Reset Defaults"
        )
        self.reset_button.setObjectName(
            "settingsSecondaryButton"
        )

        self.save_button = QPushButton(
            "Save Settings"
        )
        self.save_button.setObjectName(
            "settingsPrimaryButton"
        )

        actions.addStretch()
        actions.addWidget(
            self.reset_button
        )
        actions.addWidget(
            self.save_button
        )

        root.addLayout(
            actions
        )

        self.status_label = QLabel(
            ""
        )
        self.status_label.setObjectName(
            "settingsStatus"
        )
        root.addWidget(
            self.status_label
        )

        self.save_button.clicked.connect(
            self.save_settings
        )
        self.reset_button.clicked.connect(
            self.reset_defaults
        )

        self.setStyleSheet(
            """
            #settingsPage {
                background: #05070b;
            }

            #settingsTitle {
                color: #f4f8ff;
                font-size: 26px;
                font-weight: 700;
            }

            #settingsSubtitle {
                color: #76849a;
                font-size: 13px;
            }

            #settingsCard {
                background: #0b1018;
                border: 1px solid #1a2638;
                border-radius: 14px;
            }

            #settingsCardTitle {
                color: #ecf3ff;
                font-size: 16px;
                font-weight: 650;
            }

            #settingsFieldLabel {
                color: #aab7ca;
                font-size: 12px;
                font-weight: 600;
            }

            #settingsNote {
                color: #68778d;
                font-size: 11px;
            }

            QLineEdit,
            QComboBox {
                background: #080d14;
                color: #edf4ff;
                border: 1px solid #223149;
                border-radius: 8px;
                padding: 9px 11px;
                min-height: 20px;
            }

            QLineEdit:focus,
            QComboBox:focus {
                border: 1px solid #617cff;
            }

            QCheckBox {
                color: #d4dceb;
                spacing: 9px;
                padding: 5px 0;
            }

            #settingsPrimaryButton {
                background: #5577ff;
                color: white;
                border: none;
                border-radius: 9px;
                padding: 10px 18px;
                font-weight: 650;
            }

            #settingsPrimaryButton:hover {
                background: #6686ff;
            }

            #settingsSecondaryButton {
                background: #0d141f;
                color: #c7d1df;
                border: 1px solid #28364a;
                border-radius: 9px;
                padding: 10px 18px;
                font-weight: 600;
            }

            #settingsSecondaryButton:hover {
                background: #141e2c;
            }

            #settingsStatus {
                color: #7d91ad;
                font-size: 11px;
            }

            QScrollArea {
                background: transparent;
                border: none;
            }
            """
        )

    def _make_card(
        self,
        title,
    ):
        card = QFrame()
        card.setObjectName(
            "settingsCard"
        )

        layout = QVBoxLayout(
            card
        )
        layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )
        layout.setSpacing(10)

        title_label = QLabel(
            title
        )
        title_label.setObjectName(
            "settingsCardTitle"
        )

        layout.addWidget(
            title_label
        )

        return card

    def _field_label(
        self,
        text,
    ):
        label = QLabel(text)
        label.setObjectName(
            "settingsFieldLabel"
        )
        return label

    # =====================================================
    # DATA
    # =====================================================

    def load_settings(
        self,
    ):
        settings = (
            self.settings_manager.all()
        )

        self.wake_phrase_input.setText(
            str(
                settings.get(
                    "wake_phrase",
                    DEFAULT_SETTINGS[
                        "wake_phrase"
                    ],
                )
            )
        )

        self.speech_checkbox.setChecked(
            bool(
                settings.get(
                    "speech_enabled",
                    True,
                )
            )
        )

        self.mic_default_checkbox.setChecked(
            bool(
                settings.get(
                    "always_on_mic_default",
                    False,
                )
            )
        )

        model = str(
            settings.get(
                "ai_model",
                "qwen3:4b",
            )
        ).strip()

        self.ai_model_combo.setCurrentText(
            model
        )

        self.start_minimized_checkbox.setChecked(
            bool(
                settings.get(
                    "start_minimized",
                    False,
                )
            )
        )

        self.status_label.setText(
            "Saved preferences loaded."
        )

    def collect_settings(
        self,
    ):
        wake_phrase = (
            self.wake_phrase_input
            .text()
            .strip()
            .lower()
        )

        if not wake_phrase:
            raise ValueError(
                "Wake phrase cannot be empty."
            )

        model = (
            self.ai_model_combo
            .currentText()
            .strip()
        )

        if not model:
            raise ValueError(
                "AI model cannot be empty."
            )

        return {
            "wake_phrase":
                wake_phrase,
            "always_on_mic_default":
                self.mic_default_checkbox
                .isChecked(),
            "speech_enabled":
                self.speech_checkbox
                .isChecked(),
            "ai_model":
                model,
            "start_minimized":
                self.start_minimized_checkbox
                .isChecked(),
        }

    def save_settings(
        self,
    ):
        try:
            values = (
                self.collect_settings()
            )

            saved = (
                self.settings_manager.update(
                    values
                )
            )

            self.status_label.setText(
                "Settings saved."
            )

            self.settings_saved.emit(
                saved
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Settings",
                str(error),
            )

    def reset_defaults(
        self,
    ):
        try:
            settings = (
                self.settings_manager.reset()
            )

            self.load_settings()

            self.status_label.setText(
                "Default settings restored."
            )

            self.settings_saved.emit(
                settings
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Settings",
                str(error),
            )