from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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

from actions.desktop_actions import (
    delete_item,
    execute_command,
    prepare_delete,
)

from actions.system_actions import (
    execute_system_command,
    perform_power_action,
    prepare_power_action,
)

from voice.voice_worker import VoiceWorker
from voice.speech_engine import SpeechEngine
from voice.speech_worker import SpeechWorker

from brain.command_router import CommandRouter
from brain.ai_request_worker import AIRequestWorker


class AssistantPage(QFrame):

    def __init__(
        self,
        voice_engine,
        ai_controller=None
    ):
        super().__init__()

        # =================================================
        # ENGINES
        # =================================================

        self.voice_engine = voice_engine
        self.speech_engine = SpeechEngine()
        self.command_router = CommandRouter()
        self.ai_controller = ai_controller

        self.voice_worker = None
        self.ai_worker = None
        self.speech_worker = None
        self.pending_ai_text = ""
        self.pending_ai_from_voice = False

        self.setObjectName("page")

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            32,
            24,
            32,
            26
        )

        main_layout.setSpacing(14)

        # =================================================
        # TITLE
        # =================================================

        title = QLabel(
            "WizzArc Assistant"
        )

        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "Chat naturally, run commands, or use voice control."
        )

        description.setObjectName(
            "pageDescription"
        )

        main_layout.addWidget(
            title
        )

        main_layout.addWidget(
            description
        )

        # =================================================
        # CHAT CONTAINER
        # =================================================

        chat_container = QFrame()

        chat_container.setObjectName(
            "assistantChat"
        )

        chat_container_layout = QVBoxLayout(
            chat_container
        )

        chat_container_layout.setContentsMargins(
            0,
            0,
            0,
            0
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

        # =================================================
        # CHAT WIDGET
        # =================================================

        self.chat_widget = QWidget()

        self.chat_layout = QVBoxLayout(
            self.chat_widget
        )

        self.chat_layout.setContentsMargins(
            22,
            20,
            22,
            20
        )

        self.chat_layout.setSpacing(
            14
        )

        self.chat_layout.addStretch()

        self.scroll_area.setWidget(
            self.chat_widget
        )

        chat_container_layout.addWidget(
            self.scroll_area
        )

        main_layout.addWidget(
            chat_container,
            1
        )

        # =================================================
        # INPUT FRAME
        # =================================================

        input_frame = QFrame()

        input_frame.setObjectName(
            "assistantInputFrame"
        )

        input_layout = QHBoxLayout(
            input_frame
        )

        input_layout.setContentsMargins(
            14,
            12,
            14,
            12
        )

        input_layout.setSpacing(
            10
        )

        # =================================================
        # MESSAGE INPUT
        # =================================================

        self.message_input = QLineEdit()

        self.message_input.setPlaceholderText(
            "Ask anything or type a command..."
        )

        self.message_input.setObjectName(
            "assistantInput"
        )

        self.message_input.returnPressed.connect(
            self.send_message
        )

        # =================================================
        # MIC BUTTON
        # =================================================

        self.mic_button = QPushButton(
            "Voice"
        )

        self.mic_button.setObjectName(
            "assistantMicButton"
        )

        self.mic_button.clicked.connect(
            self.start_voice
        )

        # =================================================
        # SEND BUTTON
        # =================================================

        self.send_button = QPushButton(
            "Send  →"
        )

        self.send_button.setObjectName(
            "assistantSendButton"
        )

        self.send_button.clicked.connect(
            self.send_message
        )

        input_layout.addWidget(
            self.message_input,
            1
        )

        input_layout.addWidget(
            self.mic_button
        )

        input_layout.addWidget(
            self.send_button
        )

        main_layout.addWidget(
            input_frame
        )

        # =================================================
        # INITIAL MESSAGE
        # =================================================

        self.add_assistant_message(
            "WizzArc is ready. Ask a question, run a command, or use voice."
        )

    # =====================================================
    # START VOICE
    # =====================================================

    def start_voice(self):

        # Prevent multiple voice workers
        if (
            self.voice_worker is not None
            and self.voice_worker.isRunning()
        ):
            return

        self.mic_button.setText(
            "Listening..."
        )

        self.mic_button.setEnabled(
            False
        )

        self.voice_worker = VoiceWorker(
            self.voice_engine
        )

        self.voice_worker.result_ready.connect(
            self.voice_result
        )

        self.voice_worker.error_occurred.connect(
            self.voice_error
        )

        self.voice_worker.finished.connect(
            self.voice_finished
        )

        self.voice_worker.start()

    # =====================================================
    # VOICE RESULT
    # =====================================================

    def voice_result(
        self,
        text
    ):

        text = text.strip()

        # Nothing detected
        if not text:

            self.add_assistant_message(
                "I couldn't hear that clearly."
            )

            return

        # Voice engine error
        if text.startswith(
            "ERROR:"
        ):

            self.add_assistant_message(
                text
            )

            return

        print(
            f"Assistant voice heard: {text}"
        )

        # Put detected speech into input
        self.message_input.setText(
            text
        )

        # Process as voice command
        self.send_message(
            from_voice=True
        )

    # =====================================================
    # VOICE ERROR
    # =====================================================

    def voice_error(
        self,
        error
    ):

        self.add_assistant_message(
            f"Voice error: {error}"
        )

    # =====================================================
    # VOICE FINISHED
    # =====================================================

    def voice_finished(self):

        self.mic_button.setText(
            "Voice"
        )

        self.mic_button.setEnabled(
            True
        )

    # =====================================================
    # SEND MESSAGE
    # =====================================================

    def send_message(
        self,
        from_voice=False
    ):

        # PySide button clicked() can send a bool
        if not isinstance(
            from_voice,
            bool
        ):
            from_voice = False

        # =================================================
        # GET ORIGINAL COMMAND
        # =================================================

        original_command = (
            self.message_input
            .text()
            .strip()
        )

        if not original_command:
            return

        # User bubble should show what user actually said
        self.add_user_message(
            original_command
        )

        self.message_input.clear()

        # =================================================
        # PHASE 8 AI CONTROLLER - BACKGROUND THREAD
        # =================================================

        if self.ai_controller is not None:

            self.start_ai_request(
                original_command,
                from_voice=from_voice,
            )

            return

        # No AI controller available: use legacy commands.
        self.run_legacy_message(
            original_command,
            from_voice=from_voice,
        )

    # =====================================================
    # START AI REQUEST
    # =====================================================

    def start_ai_request(
        self,
        original_command,
        from_voice=False,
    ):

        # Avoid two simultaneous local-model requests.
        if (
            self.ai_worker is not None
            and
            self.ai_worker.isRunning()
        ):
            self.add_assistant_message(
                "I'm still processing the previous request."
            )
            return

        self.pending_ai_text = str(
            original_command
        )

        self.pending_ai_from_voice = bool(
            from_voice
        )

        self.send_button.setEnabled(
            False
        )

        self.message_input.setEnabled(
            False
        )

        self.send_button.setText(
            "Thinking..."
        )

        self.ai_worker = AIRequestWorker(
            self.ai_controller,
            original_command,
            self,
        )

        self.ai_worker.result_ready.connect(
            self.ai_result_ready
        )

        self.ai_worker.error_occurred.connect(
            self.ai_error
        )

        self.ai_worker.finished.connect(
            self.ai_request_finished
        )

        self.ai_worker.start()

    # =====================================================
    # AI RESULT
    # =====================================================

    def ai_result_ready(
        self,
        ai_result
    ):

        if ai_result.success:

            result = (
                ai_result.text
                or "Done."
            )

            self.add_assistant_message(
                result
            )

            # Improvement #6 foundation:
            # every AI reply is both written and spoken,
            # whether the user typed or used the microphone.
            self.speak_reply(
                result
            )

            return

        print(
            "AIController fallback:",
            ai_result.error
        )

        # If the AI cannot map an old fixed command,
        # preserve legacy CommandRouter behavior.
        self.run_legacy_message(
            self.pending_ai_text,
            from_voice=self.pending_ai_from_voice,
        )

    # =====================================================
    # AI ERROR
    # =====================================================

    def ai_error(
        self,
        error
    ):

        self.add_assistant_message(
            f"AI error: {error}"
        )

    # =====================================================
    # AI FINISHED
    # =====================================================

    def ai_request_finished(
        self
    ):

        self.send_button.setEnabled(
            True
        )

        self.message_input.setEnabled(
            True
        )

        self.send_button.setText(
            "Send  →"
        )

        self.message_input.setFocus()

    # =====================================================
    # LEGACY MESSAGE FALLBACK
    # =====================================================

    def run_legacy_message(
        self,
        original_command,
        from_voice=False,
    ):

        command = self.command_router.route(
            original_command
        )

        print(
            f"Assistant Router: "
            f"'{original_command}' -> '{command}'"
        )

        if not command:

            result = (
                "I couldn't understand that command."
            )

            self.add_assistant_message(
                result
            )

            self.speak_reply(
                result
            )

            return

        result = self.process_command(
            command
        )

        if not result:
            return

        self.add_assistant_message(
            result
        )

        speech = self.get_voice_response(
            command,
            result
        )

        if speech:

            self.speak_reply(
                speech
            )

    # =====================================================
    # SPEAK REPLY WITHOUT FREEZING UI
    # =====================================================

    def speak_reply(
        self,
        text
    ):

        text = str(
            text
        ).strip()

        if not text:
            return

        # Do not overlap two spoken replies.
        if (
            self.speech_worker is not None
            and
            self.speech_worker.isRunning()
        ):
            return

        self.speech_worker = SpeechWorker(
            text,
            self,
        )

        self.speech_worker.error_occurred.connect(
            lambda error:
            print(
                "Assistant speech error:",
                error
            )
        )

        self.speech_worker.start()

    # =====================================================
    # VOICE RESPONSE GENERATOR
    # =====================================================

    def get_voice_response(
        self,
        command,
        result
    ):

        command = (
            command
            .lower()
            .strip()
        )

        # =================================================
        # FIXED RESPONSES
        # =================================================

        responses = {

            # APPS

            "open chrome":
                "Opening Chrome.",

            "open edge":
                "Opening Edge.",

            "open calculator":
                "Opening Calculator.",

            "open notepad":
                "Opening Notepad.",

            "open paint":
                "Opening Paint.",

            "open vscode":
                "Opening Visual Studio Code.",

            "open visual studio code":
                "Opening Visual Studio Code.",


            # FOLDERS

            "open downloads":
                "Opening Downloads.",

            "open documents":
                "Opening Documents.",

            "open desktop":
                "Opening Desktop.",

            "open pictures":
                "Opening Pictures.",

            "open music":
                "Opening Music.",

            "open videos":
                "Opening Videos.",


            # AUDIO

            "volume up":
                "Increasing volume.",

            "volume down":
                "Decreasing volume.",

            "mute":
                "Muting audio.",

            "unmute":
                "Unmuting audio.",


            # DISPLAY

            "brightness up":
                "Increasing brightness.",

            "brightness down":
                "Decreasing brightness.",


            # CONNECTIVITY

            "wifi on":
                "Turning Wi-Fi on.",

            "wifi off":
                "Turning Wi-Fi off.",

            "bluetooth on":
                "Turning Bluetooth on.",

            "bluetooth off":
                "Turning Bluetooth off.",


            # OTHER

            "take screenshot":
                "Taking a screenshot.",

            "lock computer":
                "Locking your computer.",
        }

        # =================================================
        # VOLUME VALUE
        # =================================================

        if command.startswith(
            "set volume to "
        ):

            value = command.replace(
                "set volume to ",
                ""
            )

            return (
                f"Setting volume to {value} percent."
            )

        # =================================================
        # BRIGHTNESS VALUE
        # =================================================

        if command.startswith(
            "set brightness to "
        ):

            value = command.replace(
                "set brightness to ",
                ""
            )

            return (
                f"Setting brightness to {value} percent."
            )

        # =================================================
        # NORMAL FIXED RESPONSE
        # =================================================

        if command in responses:

            return responses[
                command
            ]

        # Otherwise speak actual action result
        return str(
            result
        )

    # =====================================================
    # COMMAND PROCESSING
    # =====================================================

    def process_command(
        self,
        command
    ):

        try:

            # =================================================
            # DELETE
            # =================================================

            delete_target, delete_error = (
                prepare_delete(
                    command
                )
            )

            if delete_error:

                return delete_error

            if delete_target:

                answer = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    (
                        f"Move '{delete_target.name}' "
                        "to Recycle Bin?"
                    ),
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Cancel,
                )

                if (
                    answer
                    == QMessageBox.StandardButton.Yes
                ):

                    return delete_item(
                        delete_target
                    )

                return (
                    "Delete cancelled."
                )

            # =================================================
            # POWER ACTION
            # =================================================

            power_action = (
                prepare_power_action(
                    command
                )
            )

            if power_action:

                if power_action == "shutdown":

                    title = (
                        "Confirm Shutdown"
                    )

                    message = (
                        "Are you sure you want to "
                        "shut down this computer?"
                    )

                else:

                    title = (
                        "Confirm Restart"
                    )

                    message = (
                        "Are you sure you want to "
                        "restart this computer?"
                    )

                answer = QMessageBox.question(
                    self,
                    title,
                    message,
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Cancel,
                )

                if (
                    answer
                    == QMessageBox.StandardButton.Yes
                ):

                    return perform_power_action(
                        power_action
                    )

                return (
                    f"{power_action.title()} cancelled."
                )

            # =================================================
            # SYSTEM COMMAND
            # =================================================

            system_result = (
                execute_system_command(
                    command
                )
            )

            if system_result is not None:

                return system_result

            # =================================================
            # DESKTOP COMMAND
            # =================================================

            return execute_command(
                command
            )

        except Exception as error:

            return (
                f"Something went wrong: {error}"
            )

    # =====================================================
    # USER MESSAGE
    # =====================================================

    def add_user_message(
        self,
        message
    ):

        row = QHBoxLayout()

        row.addStretch()

        bubble = QLabel(
            str(message)
        )

        bubble.setWordWrap(
            True
        )

        bubble.setMaximumWidth(
            560
        )

        bubble.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        bubble.setObjectName(
            "userBubble"
        )

        row.addWidget(
            bubble
        )

        self.insert_chat_row(
            row
        )

    # =====================================================
    # ASSISTANT MESSAGE
    # =====================================================

    def add_assistant_message(
        self,
        message
    ):

        row = QHBoxLayout()

        bubble = QLabel(
            str(message)
        )

        bubble.setWordWrap(
            True
        )

        bubble.setMaximumWidth(
            620
        )

        bubble.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        bubble.setObjectName(
            "assistantBubble"
        )

        row.addWidget(
            bubble
        )

        row.addStretch()

        self.insert_chat_row(
            row
        )

    # =====================================================
    # INSERT CHAT ROW
    # =====================================================

    def insert_chat_row(
        self,
        row
    ):

        position = (
            self.chat_layout.count()
            - 1
        )

        self.chat_layout.insertLayout(
            position,
            row
        )

        # Automatically scroll down after layout updates
        scrollbar = (
            self.scroll_area
            .verticalScrollBar()
        )

        scrollbar.rangeChanged.connect(
            lambda minimum, maximum:
            scrollbar.setValue(
                maximum
            )
        )