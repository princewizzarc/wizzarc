from actions.automation_manager import (
    restore_saved_automations
)

from actions.desktop_actions import (
    execute_command
)
from pathlib import Path
from core.crash_logger import (
    install_global_error_handlers,
    log_runtime_error,
)
from core.settings_manager import SETTINGS_MANAGER
from core.activity_logger import log_activity
from core.action_safety import DangerousAction
from core.app_paths import resource_path
import math
import sys

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QIcon, QColor, QPainter, QPen, QRadialGradient, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from voice.voice_engine import VoiceEngine
from voice.voice_worker import VoiceWorker
from voice.wake_listener_worker import WakeListenerWorker
from voice.speech_engine import SpeechEngine
from voice.speech_worker import SpeechWorker

from brain.command_router import CommandRouter
from brain.custom_command_executor import execute_wizzarc_command
from brain.command_registry import resolve_registered_command
from brain.ai_engine import AI_ENGINE
from brain.ollama_backend import connect_ollama
from brain.ai_controller import AIController
from brain.ai_request_worker import AIRequestWorker

from actions.desktop_actions import (
    delete_item,
    execute_command,
    prepare_delete,
    list_items,
)

from actions.file_system_manager import (
    get_available_drives,
    list_drive_items,
)

from actions.system_actions import (
    execute_system_command,
    perform_power_action,
    prepare_power_action,
    set_volume,
    mute_volume,
    unmute_volume,
    set_brightness,
    take_screenshot,
    set_wifi,
    set_bluetooth,
    lock_computer,
)

from ui.assistant_page import AssistantPage
from ui.ai_orb import AIOrb
from ui.commands_page import CommandsPage
from ui.files_page import FilesPage
from ui.custom_apps_page import CustomAppsPage
from ui.settings_page import SettingsPage
from ui.activity_page import ActivityPage


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = resource_path("assets", "wizzarc.ico")
LOGO_PATH = resource_path("assets", "wizzarc_logo.png")




# =========================================================
# SUBTLE ANIMATED HERO PANEL - IMPROVEMENT #7
# =========================================================

class AnimatedHeroPanel(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.phase = 0.0

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(
            self.update_panel_animation
        )
        self.animation_timer.start(
            45
        )

    def update_panel_animation(self):

        self.phase += 0.035

        if self.phase >= 360:
            self.phase = 0.0

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        w = self.width()
        h = self.height()

        rect = QRectF(
            1,
            1,
            w - 2,
            h - 2
        )

        # Deep space background
        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor(
                7,
                8,
                18,
                250
            )
        )

        painter.drawRoundedRect(
            rect,
            22,
            22
        )

        # Moving violet-blue ambient glow
        glow_x = (
            w * 0.50
            + math.sin(
                self.phase
            )
            * w * 0.10
        )

        glow_y = (
            h * 0.44
            + math.cos(
                self.phase * 0.75
            )
            * h * 0.06
        )

        glow = QRadialGradient(
            glow_x,
            glow_y,
            max(
                w,
                h
            )
            * 0.62
        )

        glow.setColorAt(
            0.0,
            QColor(
                115,
                65,
                255,
                35
            )
        )

        glow.setColorAt(
            0.42,
            QColor(
                45,
                105,
                255,
                16
            )
        )

        glow.setColorAt(
            1.0,
            QColor(
                0,
                0,
                0,
                0
            )
        )

        painter.setBrush(
            glow
        )

        painter.drawRoundedRect(
            rect,
            22,
            22
        )

        # Tiny drifting star particles
        for index in range(22):

            seed_x = (
                (
                    index * 73
                    + 31
                )
                % 100
            ) / 100.0

            seed_y = (
                (
                    index * 47
                    + 19
                )
                % 100
            ) / 100.0

            drift = (
                math.sin(
                    self.phase
                    * (
                        0.6
                        + (
                            index % 5
                        )
                        * 0.08
                    )
                    + index
                )
                * 4
            )

            x = (
                14
                + seed_x
                * (
                    w - 28
                )
                + drift
            )

            y = (
                16
                + seed_y
                * (
                    h - 32
                )
            )

            alpha = int(
                45
                + (
                    math.sin(
                        self.phase * 1.2
                        + index
                    )
                    + 1
                )
                * 50
            )

            color = (
                QColor(
                    140,
                    90,
                    255,
                    alpha
                )
                if index % 2 == 0
                else QColor(
                    65,
                    145,
                    255,
                    alpha
                )
            )

            painter.setBrush(
                color
            )

            painter.drawEllipse(
                QPointF(
                    x,
                    y
                ),
                1.2
                + (
                    index % 3
                )
                * 0.4,
                1.2
                + (
                    index % 3
                )
                * 0.4
            )

        # Subtle left/right wave field
        wave_pen_left = QPen(
            QColor(
                55,
                120,
                255,
                38
            )
        )

        wave_pen_left.setWidthF(
            1.0
        )

        wave_pen_right = QPen(
            QColor(
                150,
                70,
                255,
                34
            )
        )

        wave_pen_right.setWidthF(
            1.0
        )

        for side in (
            "left",
            "right",
        ):

            painter.setPen(
                wave_pen_left
                if side == "left"
                else wave_pen_right
            )

            for line_index in range(5):

                points = []

                for step in range(45):

                    t = (
                        step / 44.0
                    )

                    if side == "left":

                        x = (
                            t
                            * w
                            * 0.34
                        )

                    else:

                        x = (
                            w
                            - t
                            * w
                            * 0.34
                        )

                    base_y = (
                        h
                        * 0.53
                    )

                    amplitude = (
                        h
                        * (
                            0.045
                            + line_index
                            * 0.009
                        )
                    )

                    y = (
                        base_y
                        + math.sin(
                            t * 9.0
                            + self.phase
                            * 1.4
                            + line_index
                        )
                        * amplitude
                    )

                    points.append(
                        QPointF(
                            x,
                            y
                        )
                    )

                for i in range(
                    len(points) - 1
                ):

                    painter.drawLine(
                        points[i],
                        points[i + 1]
                    )

        # Breathing neon border
        border_alpha = int(
            90
            + (
                math.sin(
                    self.phase * 1.25
                )
                + 1
            )
            * 28
        )

        border_pen = QPen(
            QColor(
                104,
                70,
                255,
                border_alpha
            )
        )

        border_pen.setWidthF(
            1.3
        )

        painter.setPen(
            border_pen
        )

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.drawRoundedRect(
            rect,
            22,
            22
        )


# =========================================================
# MAIN WINDOW
# =========================================================

class WizzArc(QMainWindow):

    def __init__(self):
        super().__init__()

        # =================================================
        # WINDOW
        # =================================================

        self.setWindowTitle("WizzArc")

        if ICON_PATH.exists():
            self.setWindowIcon(
                QIcon(str(ICON_PATH))
            )

        self.resize(1200, 750)
        self.setMinimumSize(950, 600)

        # =================================================
        # PHASE 9.5 - USER SETTINGS
        # =================================================

        self.settings_manager = SETTINGS_MANAGER
        self.user_settings = (
            self.settings_manager.all()
        )

        self.wake_phrase = str(
            self.user_settings.get(
                "wake_phrase",
                "wizzarc",
            )
        ).strip().lower() or "wizzarc"

        self.speech_enabled = bool(
            self.user_settings.get(
                "speech_enabled",
                True,
            )
        )

        self.always_on_mic_default = bool(
            self.user_settings.get(
                "always_on_mic_default",
                False,
            )
        )

        self.ai_model = str(
            self.user_settings.get(
                "ai_model",
                "qwen3:4b",
            )
        ).strip() or "qwen3:4b"

        self.start_minimized = bool(
            self.user_settings.get(
                "start_minimized",
                False,
            )
        )

        # =================================================
        # ENGINES
        # =================================================

        self.voice_engine = VoiceEngine()
        self.speech_engine = SpeechEngine()
        self.command_router = CommandRouter()

        # =================================================
        # PHASE 8 AI CONTROLLER
        # =================================================

        self.ai_controller = None
        self.ai_backend_error = None

        try:
            connect_ollama(
                AI_ENGINE,
                model=self.ai_model,
            )

            self.ai_controller = AIController(
                AI_ENGINE,
                execute_wizzarc_command
            )

        except Exception as error:
            self.ai_backend_error = str(
                error
            )

            print(
                "WizzArc AI Controller startup error:",
                error
            )

        self.home_voice_worker = None
        self.home_wake_worker = None
        self.home_ai_worker = None
        self.home_speech_worker = None

        # Improvement #6 + Phase 9.5
        self.always_on_mic_enabled = False

        self.pending_home_ai_text = ""

        # Used by Commands button
        self.previous_page_index = 0

        self.build_ui()
        self.refresh_home_status_ui()

        # Apply saved mic preference only after UI controls exist.
        if self.always_on_mic_default:
            QTimer.singleShot(
                0,
                self.enable_always_on_mic,
            )

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        # =================================================
        # SIDEBAR
        # =================================================

        sidebar = QFrame()

        sidebar.setFixedWidth(
            230
        )

        sidebar.setObjectName(
            "sidebar"
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        sidebar_layout.setContentsMargins(
            20,
            25,
            20,
            25
        )

        sidebar_layout.setSpacing(
            10
        )

        # =================================================
        # LOGO
        # =================================================

        logo = QLabel(
            "WizzArc"
        )

        logo.setObjectName(
            "logo"
        )

        sidebar_layout.addWidget(
            logo
        )

        subtitle = QLabel(
            "Desktop AI Assistant"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        sidebar_layout.addWidget(
            subtitle
        )

        sidebar_layout.addSpacing(
            25
        )

        # =================================================
        # RIGHT SIDE
        # =================================================

        right_panel = QWidget()

        right_layout = QVBoxLayout(
            right_panel
        )

        right_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        right_layout.setSpacing(
            0
        )

        # =================================================
        # TOP BAR
        # =================================================

        top_bar = QFrame()

        top_bar.setObjectName(
            "topBar"
        )

        top_bar.setFixedHeight(
            58
        )

        top_bar_layout = QHBoxLayout(
            top_bar
        )

        top_bar_layout.setContentsMargins(
            20,
            8,
            28,
            8
        )

        self.top_page_title = QLabel(
            "Home"
        )
        self.top_page_title.setObjectName(
            "topPageTitle"
        )

        self.top_page_subtitle = QLabel(
            "Desktop AI control center"
        )
        self.top_page_subtitle.setObjectName(
            "topPageSubtitle"
        )

        top_identity = QVBoxLayout()
        top_identity.setSpacing(
            0
        )
        top_identity.addWidget(
            self.top_page_title
        )
        top_identity.addWidget(
            self.top_page_subtitle
        )

        top_bar_layout.addLayout(
            top_identity
        )

        top_bar_layout.addStretch()

        self.version_badge = QLabel(
            "WizzArc  •  Launch Build"
        )
        self.version_badge.setObjectName(
            "versionBadge"
        )
        self.version_badge.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        top_bar_layout.addWidget(
            self.version_badge
        )

        # =================================================
        # COMMANDS BUTTON
        # =================================================

        self.commands_button = QPushButton(
            "Commands"
        )

        self.commands_button.setObjectName(
            "commandsButton"
        )

        self.commands_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.commands_button.clicked.connect(
            self.toggle_commands_page
        )

        top_bar_layout.addWidget(
            self.commands_button
        )

        right_layout.addWidget(
            top_bar
        )

        # =================================================
        # PAGE STACK
        # =================================================

        self.pages = QStackedWidget()

        # HOME - 0
        self.pages.addWidget(
            self.create_home_page()
        )

        # ASSISTANT - 1
        self.assistant_page = AssistantPage(
            self.voice_engine,
            self.ai_controller
        )

        self.pages.addWidget(
            self.assistant_page
        )

        # FILES - 2
        self.files_page = FilesPage()

        self.pages.addWidget(
            self.files_page
        )

        # APPS - 3
        # Improvement #8 - Custom App + Command Manager
        self.custom_apps_page = CustomAppsPage()

        self.pages.addWidget(
            self.custom_apps_page
        )

        # SYSTEM - 4
        self.pages.addWidget(
            self.create_system_page()
        )

        # AUTOMATION - 5
        self.pages.addWidget(
            self.create_simple_page(
                "Automation",
                (
                    "Create scheduled and multi-step "
                    "desktop automations."
                )
            )
        )

        # SCREEN - 6
        self.pages.addWidget(
            self.create_simple_page(
                "Screen",
                (
                    "Screen understanding and visual "
                    "actions will appear here."
                )
            )
        )

        # ACTIVITY - 7
        self.activity_page = ActivityPage(
            parent=self,
        )
        self.pages.addWidget(
            self.activity_page
        )

        # PERMISSIONS - 8
        self.pages.addWidget(
            self.create_simple_page(
                "Permissions",
                "Manage WizzArc permissions."
            )
        )

        # SETTINGS - 9
        self.settings_page = SettingsPage(
            self.settings_manager,
            parent=self,
        )
        self.settings_page.settings_saved.connect(
            self.apply_saved_settings
        )
        self.pages.addWidget(
            self.settings_page
        )

        # =================================================
        # COMMANDS PAGE
        # Not part of sidebar
        # =================================================

        self.commands_page = CommandsPage()

        self.commands_page_index = (
            self.pages.addWidget(
                self.commands_page
            )
        )

        right_layout.addWidget(
            self.pages,
            1
        )

        # =================================================
        # SIDEBAR MENU
        # =================================================

        self.page_names = [
            "Home",
            "Assistant",
            "Files",
            "Apps",
            "System",
            "Automation",
            "Screen",
            "Activity",
            "Permissions",
            "Settings",
        ]

        self.page_subtitles = [
            "Desktop AI control center",
            "Chat, voice, and natural commands",
            "Browse files, folders, and drives",
            "Manage custom apps and commands",
            "Audio, display, and system controls",
            "Scheduled and multi-step actions",
            "Screen understanding and visual tools",
            "Recent commands, actions, and errors",
            "Review security and access controls",
            "Personalize WizzArc behavior",
        ]

        menu_items = self.page_names

        self.menu_buttons = []

        for index, item in enumerate(
            menu_items
        ):

            button = QPushButton(
                item
            )

            button.setObjectName(
                "menuButton"
            )

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            button.setMinimumHeight(
                38
            )

            button.clicked.connect(
                lambda checked=False, i=index:
                self.change_page(i)
            )

            sidebar_layout.addWidget(
                button
            )

            self.menu_buttons.append(
                button
            )

        sidebar_layout.addStretch()

        # =================================================
        # VERSION
        # =================================================

        version = QLabel(
            "WizzArc v0.5"
        )

        version.setObjectName(
            "version"
        )

        sidebar_layout.addWidget(
            version
        )

        # =================================================
        # ADD SIDEBAR + RIGHT PANEL
        # =================================================

        main_layout.addWidget(
            sidebar
        )

        main_layout.addWidget(
            right_panel,
            1
        )

        self.change_page(
            0
        )

        # =================================================
        # GLOBAL STYLE
        # =================================================

        self.setStyleSheet(
            """

            QMainWindow {
                background-color: #05070b;
            }

            QWidget {
                font-family: Segoe UI;
            }

            /* =============================================
               PHASE 9.8 - FINAL NAVIGATION POLISH
               ============================================= */

            #topPageTitle {
                color: #f8f7ff;
                font-size: 15px;
                font-weight: 700;
            }

            #topPageSubtitle {
                color: #717b94;
                font-size: 10px;
            }

            #versionBadge {
                color: #aaa6d9;
                background-color: #0d0e1b;
                border: 1px solid #272844;
                border-radius: 11px;
                padding: 5px 10px;
                font-size: 10px;
                font-weight: 600;
                margin-right: 8px;
            }

            #menuButton {
                background-color: transparent;
                color: #929ab0;
                border: 1px solid transparent;
                border-radius: 10px;
                padding: 8px 12px;
                text-align: left;
                font-size: 12px;
                font-weight: 600;
            }

            #menuButton:pressed {
                background-color: #1d1737;
            }

            #menuButton:disabled {
                color: #4d5365;
                background-color: transparent;
            }

            #pageTitle {
                color: #f6f5ff;
                font-size: 24px;
                font-weight: 700;
            }

            #pageDescription {
                color: #8d95aa;
                font-size: 12px;
            }

            QPushButton:disabled {
                color: #5f6678;
                background-color: #0c0e16;
                border-color: #202536;
            }

            QToolTip {
                color: #f4f2ff;
                background-color: #101322;
                border: 1px solid #34395b;
                padding: 5px 7px;
            }

            /* =============================================
               TOP BAR
               ============================================= */

            #topBar {
                background-color: #05070b;
                border-bottom: 1px solid #171f2b;
            }

            #commandsButton {
                background-color: #0d131c;
                color: #dce5f3;

                border: 1px solid #233147;
                border-radius: 9px;

                padding: 9px 18px;

                font-size: 13px;
                font-weight: 600;
            }

            #commandsButton:hover {
                background-color: #141d2a;
                color: white;

                border: 1px solid #344763;
            }

            /* =============================================
               SIDEBAR
               ============================================= */

            #sidebar {
                background-color: #090d13;
                border-right: 1px solid #161d28;
            }

            #logo {
                color: white;
                font-size: 28px;
                font-weight: 700;
            }

            #subtitle {
                color: #7f8da3;
                font-size: 12px;
            }

            #menuButton {
                background-color: transparent;
                color: #b8c2d1;

                border: none;
                border-radius: 8px;

                padding: 11px 12px;

                text-align: left;

                font-size: 14px;
            }

            #menuButton:hover {
                background-color: #101722;
                color: white;
            }

            #menuButton[active="true"] {
                background-color: #16233a;
                color: white;
                font-weight: 600;
            }

            #version {
                color: #566276;
                font-size: 11px;
            }

            /* =============================================
               PAGE
               ============================================= */

            #page {
                background-color: #05070b;
            }

            #pageTitle {
                color: white;
                font-size: 34px;
                font-weight: 700;
            }

            #pageDescription {
                color: #8f9bad;
                font-size: 14px;
            }

            /* =============================================
               CARDS
               ============================================= */

            #assistantCard,
            #systemCard {
                background-color: #0b1018;

                border: 1px solid #1a2432;
                border-radius: 18px;
            }

            #cardTitle {
                color: white;
                font-size: 20px;
                font-weight: 600;
            }

            #cardText {
                color: #8e9aac;
                font-size: 13px;
            }

            /* =============================================
               HOME INPUT
               ============================================= */

            #commandInput {
                background-color: #080c12;

                border: 1px solid #1f2c40;
                border-radius: 10px;

                color: white;

                padding: 13px;

                font-size: 14px;
            }

            #commandInput:focus {
                border: 1px solid #5577ff;
            }

            #runButton {
                background-color: #5577ff;

                color: white;

                border: none;
                border-radius: 10px;

                padding: 12px 22px;

                font-weight: 600;
            }

            #runButton:hover {
                background-color: #6a87ff;
            }

            #micButton,
            #controlButton {
                background-color: #0f1722;

                color: white;

                border: 1px solid #223149;
                border-radius: 9px;

                padding: 10px 15px;
            }

            #micButton:hover,
            #controlButton:hover {
                background-color: #162238;
            }

            #dangerButton {
                background-color: #351a20;

                color: #ff9ba8;

                border: 1px solid #61303a;
                border-radius: 9px;

                padding: 10px 15px;
            }

            #dangerButton:hover {
                background-color: #4a222b;
            }

            #status {
                color: #718096;
                font-size: 12px;
            }

            #systemStatus {
                color: #8f9bad;
                font-size: 13px;
            }

            /* =============================================
               ASSISTANT
               ============================================= */

            #assistantChat {
                background-color: #080c12;

                border: 1px solid #1a2432;
                border-radius: 16px;
            }

            #assistantInputFrame {
                background-color: #0b1018;

                border: 1px solid #1f2c40;
                border-radius: 14px;
            }

            #assistantInput {
                background-color: transparent;

                border: none;

                color: white;

                font-size: 14px;

                padding: 10px;
            }

            #assistantInput:focus {
                border: none;
            }

            #assistantMicButton {
                background-color: #0f1722;

                color: white;

                border: 1px solid #223149;
                border-radius: 9px;

                padding: 10px 16px;
            }

            #assistantMicButton:hover {
                background-color: #1a2740;
            }

            #assistantSendButton {
                background-color: #5577ff;

                color: white;

                border: none;
                border-radius: 9px;

                padding: 10px 20px;

                font-weight: 600;
            }

            #assistantSendButton:hover {
                background-color: #6a87ff;
            }

            #userBubble {
                background-color: #5577ff;

                color: white;

                border-radius: 14px;

                padding: 12px 16px;

                font-size: 14px;
            }

            #assistantBubble {
                background-color: #101722;

                color: #e5eaf2;

                border: 1px solid #1f2b3d;
                border-radius: 14px;

                padding: 12px 16px;

                font-size: 14px;
            }

            /* =============================================
               COMMAND GUIDE
               ============================================= */

            #commandGuideSearch {
                background-color: #080c12;

                border: 1px solid #1f2c40;
                border-radius: 10px;

                color: white;

                padding: 12px 14px;

                font-size: 14px;
            }

            #commandGuideSearch:focus {
                border: 1px solid #5577ff;
            }

            #commandGuideCard {
                background-color: #0b1018;

                border: 1px solid #1a2432;
                border-radius: 14px;
            }

            #commandGuideTitle {
                color: white;

                font-size: 18px;
                font-weight: 600;

                padding-bottom: 4px;
            }

            #commandGuideRow {
                background-color: #090e16;

                border: 1px solid #162133;
                border-radius: 8px;
            }

            #commandGuideRow:hover {
                background-color: #0f1723;

                border: 1px solid #2a374b;
            }

            #commandGuideCommand {
                color: #dfe6f3;

                font-size: 13px;
                font-weight: 600;
            }

            #commandGuideAction {
                color: #8f9bad;

                font-size: 13px;
            }

            /* =============================================
               FUTURISTIC HOME
               ============================================= */

            #homeHero {
                background-color: #05070b;
                border: none;
            }

            #aiStatusTitle {
                color: #f4f8ff;
                font-size: 22px;
                font-weight: 700;
                padding-top: 2px;
            }

            #aiStatusText {
                color: #728099;
                font-size: 12px;
                padding-bottom: 4px;
            }

            #commandHint {
                color: #66748a;
                font-size: 11px;
            }



            /* =============================================
               IMPROVEMENT #7 - FUTURISTIC HOME REDESIGN
               ============================================= */

            #homeGreeting {
                color: #f7f8ff;
                font-size: 25px;
                font-weight: 700;
            }

            #homeGreetingSub {
                color: #8b96ab;
                font-size: 13px;
            }

            #aiModeBadge {
                color: #d9d8ff;
                background-color: #111326;
                border: 1px solid #2d2f52;
                border-radius: 14px;
                padding: 7px 12px;
                font-size: 12px;
                font-weight: 600;
            }

            #homeHeroCard {
                background: transparent;
                border: none;
            }

            #homeSideCard {
                min-width: 220px;
                max-width: 245px;
                background-color: #0a0c17;
                border: 1px solid #1e2740;
                border-radius: 16px;
            }

            #sideCardTitle {
                color: #f0efff;
                font-size: 15px;
                font-weight: 700;
                padding-bottom: 4px;
            }

            #statusGood {
                color: #63e6a7;
                font-size: 12px;
                padding: 6px 8px;
                background-color: #0d1717;
                border-radius: 8px;
            }

            #statusInfo {
                color: #b9c3da;
                font-size: 12px;
                padding: 6px 8px;
                background-color: #10131e;
                border-radius: 8px;
            }

            #quickActionButton {
                background-color: #111322;
                color: #dfe3f4;
                border: 1px solid #252948;
                border-radius: 9px;
                padding: 9px 11px;
                text-align: left;
                font-size: 12px;
                font-weight: 600;
            }

            #quickActionButton:hover {
                background-color: #17172d;
                border: 1px solid #6b4cff;
                color: white;
            }

            #assistantCard {
                background-color: #0a0c16;
                border: 1px solid #272443;
                border-radius: 16px;
            }

            #commandInput {
                background-color: #0d101d;
                border: 1px solid #2c3150;
                border-radius: 13px;
                color: white;
                padding: 13px 14px;
                font-size: 14px;
            }

            #commandInput:focus {
                border: 1px solid #8a5cff;
            }

            #commandHint {
                color: #68728a;
                font-size: 10px;
                padding-left: 3px;
            }

            #runButton {
                background-color: #7652ff;
                color: white;
                border: none;
                border-radius: 11px;
                padding: 12px 21px;
                font-weight: 700;
            }

            #runButton:hover {
                background-color: #8a68ff;
            }

            #micButton {
                background-color: #12162a;
                color: #ebe9ff;
                border: 1px solid #30365a;
                border-radius: 11px;
                padding: 11px 15px;
            }

            #micButton:hover {
                background-color: #191d35;
                border: 1px solid #7257ff;
            }

            #aiStatusTitle {
                color: #f5f3ff;
                font-size: 28px;
                font-weight: 800;
                padding-top: 2px;
            }

            #heroSubtitle {
                color: #8f96ad;
                font-size: 12px;
                padding-bottom: 1px;
            }

            #aiStatusText {
                color: #d9dcf3;
                font-size: 12px;
                background-color: rgba(13, 16, 31, 215);
                border: 1px solid #2b3154;
                border-radius: 15px;
                padding: 7px 15px;
                margin-bottom: 2px;
            }

            #sidebar {
                background-color: #080914;
                border-right: 1px solid #1d2038;
            }

            #logo {
                color: #f8f7ff;
                font-size: 27px;
                font-weight: 700;
            }

            #menuButton[active="true"] {
                background-color: #24184a;
                color: #ffffff;
                font-weight: 700;
                border: 1px solid #4b2c86;
            }

            #menuButton:hover {
                background-color: #14172a;
                color: white;
            }

            #topBar {
                background-color: #070812;
                border-bottom: 1px solid #1d2036;
            }

            QMainWindow,
            #page {
                background-color: #05060d;
            }

            /* =============================================
               SCROLL AREA
               ============================================= */

            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea > QWidget > QWidget {
                background: transparent;
            }

            QScrollBar:vertical {
                background: transparent;

                width: 8px;

                margin: 4px;
            }

            QScrollBar::handle:vertical {
                background: #263650;

                border-radius: 4px;

                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #42516b;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            /* =============================================
               SLIDERS
               ============================================= */

            QSlider::groove:horizontal {
                height: 6px;

                background: #1f2c40;

                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: #5577ff;

                width: 18px;

                margin: -6px 0;

                border-radius: 9px;
            }

            QSlider::sub-page:horizontal {
                background: #5577ff;

                border-radius: 3px;
            }

            """
        )


    # =====================================================
    # HOME
    # =====================================================

    def create_home_page(self):

        page = QFrame()
        page.setObjectName("page")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            28,
            24,
            28,
            26
        )
        layout.setSpacing(16)

        # =================================================
        # TOP GREETING
        # =================================================

        greeting_row = QHBoxLayout()
        greeting_row.setSpacing(12)

        greeting_box = QVBoxLayout()
        greeting_box.setSpacing(2)

        greeting = QLabel(
            "Hello, User! 👋"
        )
        greeting.setObjectName(
            "homeGreeting"
        )

        greeting_sub = QLabel(
            "I'm WizzArc, your AI assistant. How can I help you today?"
        )
        greeting_sub.setObjectName(
            "homeGreetingSub"
        )

        greeting_box.addWidget(
            greeting
        )
        greeting_box.addWidget(
            greeting_sub
        )

        greeting_row.addLayout(
            greeting_box
        )
        greeting_row.addStretch()

        self.home_ai_mode_badge = QLabel(
            "●  AI Mode"
        )
        self.home_ai_mode_badge.setObjectName(
            "aiModeBadge"
        )

        greeting_row.addWidget(
            self.home_ai_mode_badge
        )

        layout.addLayout(
            greeting_row
        )

        # =================================================
        # MAIN CONTENT
        # =================================================

        content_row = QHBoxLayout()
        content_row.setSpacing(18)

        # -------------------------------------------------
        # LEFT / CENTER AI CORE
        # -------------------------------------------------

        hero = AnimatedHeroPanel()
        hero.setObjectName(
            "homeHeroCard"
        )

        hero_layout = QVBoxLayout(
            hero
        )

        hero_layout.setContentsMargins(
            22,
            18,
            22,
            16
        )

        hero_layout.setSpacing(
            4
        )

        hero_layout.setAlignment(
            Qt.AlignmentFlag.AlignHCenter
        )

        self.ai_status_title = QLabel(
            "WizzArc Ready"
        )

        self.ai_status_title.setObjectName(
            "aiStatusTitle"
        )

        self.ai_status_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        hero_subtitle = QLabel(
            "Your AI assistant is online and ready to help!"
        )

        hero_subtitle.setObjectName(
            "heroSubtitle"
        )

        hero_subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        hero_layout.addWidget(
            self.ai_status_title
        )

        hero_layout.addWidget(
            hero_subtitle
        )

        self.ai_orb = AIOrb()

        self.ai_orb.set_state(
            "idle"
        )

        hero_layout.addWidget(
            self.ai_orb,
            1,
            Qt.AlignmentFlag.AlignHCenter
        )

        self.ai_status_text = QLabel(
            "●  Listening for your command..."
        )

        self.ai_status_text.setObjectName(
            "aiStatusText"
        )

        self.ai_status_text.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        hero_layout.addWidget(
            self.ai_status_text,
            0,
            Qt.AlignmentFlag.AlignHCenter
        )

        content_row.addWidget(
            hero,
            1
        )

        # -------------------------------------------------
        # RIGHT STATUS PANEL
        # -------------------------------------------------

        right_column = QVBoxLayout()
        right_column.setSpacing(
            12
        )

        quick_status = QFrame()
        quick_status.setObjectName(
            "homeSideCard"
        )

        quick_status_layout = QVBoxLayout(
            quick_status
        )
        quick_status_layout.setContentsMargins(
            16,
            14,
            16,
            14
        )
        quick_status_layout.setSpacing(
            9
        )

        quick_title = QLabel(
            "Quick Status"
        )
        quick_title.setObjectName(
            "sideCardTitle"
        )
        quick_status_layout.addWidget(
            quick_title
        )

        system_status = QLabel(
            "●  System   All systems normal"
        )
        system_status.setObjectName(
            "statusGood"
        )

        self.home_ai_model_status = QLabel(
            f"●  AI Model   {self.ai_model}"
        )
        self.home_ai_model_status.setObjectName(
            "statusInfo"
        )

        self.home_automation_status = QLabel(
            "●  Automation   Ready"
        )
        self.home_automation_status.setObjectName(
            "statusInfo"
        )

        self.home_screen_status = QLabel(
            "●  Screen Vision   Ready"
        )
        self.home_screen_status.setObjectName(
            "statusInfo"
        )

        self.home_mic_status = QLabel(
            "●  Microphone   Off"
        )
        self.home_mic_status.setObjectName(
            "statusInfo"
        )

        quick_status_layout.addWidget(
            system_status
        )
        quick_status_layout.addWidget(
            self.home_ai_model_status
        )
        quick_status_layout.addWidget(
            self.home_automation_status
        )
        quick_status_layout.addWidget(
            self.home_screen_status
        )
        quick_status_layout.addWidget(
            self.home_mic_status
        )

        right_column.addWidget(
            quick_status
        )

        quick_actions = QFrame()
        quick_actions.setObjectName(
            "homeSideCard"
        )

        quick_actions_layout = QVBoxLayout(
            quick_actions
        )
        quick_actions_layout.setContentsMargins(
            16,
            14,
            16,
            14
        )
        quick_actions_layout.setSpacing(
            8
        )

        quick_actions_title = QLabel(
            "Quick Actions"
        )
        quick_actions_title.setObjectName(
            "sideCardTitle"
        )

        quick_actions_layout.addWidget(
            quick_actions_title
        )

        open_chrome = QPushButton(
            "Open Chrome"
        )
        open_chrome.setObjectName(
            "quickActionButton"
        )
        open_chrome.clicked.connect(
            lambda:
            self.run_quick_command(
                "open chrome"
            )
        )

        youtube = QPushButton(
            "Search YouTube"
        )
        youtube.setObjectName(
            "quickActionButton"
        )
        youtube.clicked.connect(
            lambda:
            self.run_quick_command(
                "search youtube for python tutorial"
            )
        )

        screen_button = QPushButton(
            "What's on screen?"
        )
        screen_button.setObjectName(
            "quickActionButton"
        )
        screen_button.clicked.connect(
            lambda:
            self.run_quick_command(
                "what can you see"
            )
        )

        screenshot_button = QPushButton(
            "Take Screenshot"
        )
        screenshot_button.setObjectName(
            "quickActionButton"
        )
        screenshot_button.clicked.connect(
            lambda:
            self.run_quick_command(
                "take screenshot"
            )
        )

        quick_actions_layout.addWidget(
            open_chrome
        )
        quick_actions_layout.addWidget(
            youtube
        )
        quick_actions_layout.addWidget(
            screen_button
        )
        quick_actions_layout.addWidget(
            screenshot_button
        )

        right_column.addWidget(
            quick_actions
        )
        right_column.addStretch()

        content_row.addLayout(
            right_column
        )

        layout.addLayout(
            content_row,
            1
        )

        # =================================================
        # COMMAND BAR
        # =================================================

        assistant_card = QFrame()
        assistant_card.setObjectName(
            "assistantCard"
        )

        card_layout = QVBoxLayout(
            assistant_card
        )
        card_layout.setContentsMargins(
            18,
            14,
            18,
            14
        )
        card_layout.setSpacing(
            10
        )

        input_row = QHBoxLayout()
        input_row.setSpacing(
            10
        )

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText(
            "Type a command or ask anything..."
        )
        self.command_input.setObjectName(
            "commandInput"
        )
        self.command_input.setClearButtonEnabled(
            True
        )
        self.command_input.setToolTip(
            "Type a command or question, then press Enter."
        )
        self.command_input.returnPressed.connect(
            self.run_command
        )

        self.home_mic_button = QPushButton(
            "Mic"
        )
        self.home_mic_button.setObjectName(
            "micButton"
        )
        self.home_mic_button.clicked.connect(
            self.toggle_always_on_mic
        )

        run_button = QPushButton(
            "Send"
        )
        run_button.setObjectName(
            "runButton"
        )
        run_button.clicked.connect(
            self.run_command
        )

        input_row.addWidget(
            self.command_input,
            1
        )
        input_row.addWidget(
            self.home_mic_button
        )
        input_row.addWidget(
            run_button
        )

        card_layout.addLayout(
            input_row
        )

        command_hint = QLabel(
            "Enter to send  •  Mic button toggles wake listening"
        )
        command_hint.setObjectName(
            "commandHint"
        )
        card_layout.addWidget(
            command_hint
        )

        self.status_label = QLabel(
            "Status: WizzArc is ready"
        )
        self.status_label.setObjectName(
            "status"
        )

        card_layout.addWidget(
            self.status_label
        )

        layout.addWidget(
            assistant_card
        )

        return page

    # =====================================================
    # PHASE 9.8 - LIVE HOME STATUS
    # =====================================================

    def refresh_home_status_ui(
        self,
    ):
        if hasattr(
            self,
            "home_ai_model_status",
        ):
            self.home_ai_model_status.setText(
                f"●  AI Model   {self.ai_model}"
            )

        if hasattr(
            self,
            "home_ai_mode_badge",
        ):
            self.home_ai_mode_badge.setText(
                "●  AI Online"
                if self.ai_controller is not None
                else "●  AI Offline"
            )

        if hasattr(
            self,
            "home_mic_status",
        ):
            mic_text = (
                "Wake Listening"
                if self.always_on_mic_enabled
                else "Off"
            )
            self.home_mic_status.setText(
                f"●  Microphone   {mic_text}"
            )

    # =====================================================
    # QUICK COMMAND
    # =====================================================

    def run_quick_command(
        self,
        command
    ):

        self.command_input.setText(
            command
        )

        self.run_command()

    # =====================================================
    # SYSTEM PAGE
    # =====================================================

    def create_system_page(self):

        page = QFrame()

        page.setObjectName(
            "page"
        )

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            45,
            30,
            45,
            35
        )

        layout.setSpacing(
            15
        )

        title = QLabel(
            "System"
        )

        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "Control your computer directly from WizzArc."
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            description
        )

        # =================================================
        # AUDIO
        # =================================================

        audio_card = self.create_card()

        audio_layout = QVBoxLayout(
            audio_card
        )

        audio_layout.setContentsMargins(
            22,
            18,
            22,
            18
        )

        audio_title = QLabel(
            "Audio"
        )

        audio_title.setObjectName(
            "cardTitle"
        )

        audio_layout.addWidget(
            audio_title
        )

        volume_row = QHBoxLayout()

        volume_text = QLabel(
            "Volume"
        )

        volume_text.setObjectName(
            "cardText"
        )

        self.volume_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.volume_slider.setRange(
            0,
            100
        )

        self.volume_slider.setValue(
            50
        )

        self.volume_value = QLabel(
            "50%"
        )

        self.volume_value.setObjectName(
            "cardText"
        )

        self.volume_slider.valueChanged.connect(
            lambda value:
            self.volume_value.setText(
                f"{value}%"
            )
        )

        self.volume_slider.sliderReleased.connect(
            self.apply_volume_slider
        )

        mute_button = QPushButton(
            "Mute"
        )

        mute_button.setObjectName(
            "controlButton"
        )

        mute_button.clicked.connect(
            lambda:
            self.run_system_action(
                mute_volume
            )
        )

        unmute_button = QPushButton(
            "Unmute"
        )

        unmute_button.setObjectName(
            "controlButton"
        )

        unmute_button.clicked.connect(
            lambda:
            self.run_system_action(
                unmute_volume
            )
        )

        volume_row.addWidget(
            volume_text
        )

        volume_row.addWidget(
            self.volume_slider,
            1
        )

        volume_row.addWidget(
            self.volume_value
        )

        volume_row.addWidget(
            mute_button
        )

        volume_row.addWidget(
            unmute_button
        )

        audio_layout.addLayout(
            volume_row
        )

        layout.addWidget(
            audio_card
        )

        # =================================================
        # DISPLAY
        # =================================================

        display_card = self.create_card()

        display_layout = QVBoxLayout(
            display_card
        )

        display_layout.setContentsMargins(
            22,
            18,
            22,
            18
        )

        display_title = QLabel(
            "Display"
        )

        display_title.setObjectName(
            "cardTitle"
        )

        display_layout.addWidget(
            display_title
        )

        brightness_row = QHBoxLayout()

        brightness_text = QLabel(
            "Brightness"
        )

        brightness_text.setObjectName(
            "cardText"
        )

        self.brightness_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.brightness_slider.setRange(
            0,
            100
        )

        self.brightness_slider.setValue(
            50
        )

        self.brightness_value = QLabel(
            "50%"
        )

        self.brightness_value.setObjectName(
            "cardText"
        )

        self.brightness_slider.valueChanged.connect(
            lambda value:
            self.brightness_value.setText(
                f"{value}%"
            )
        )

        self.brightness_slider.sliderReleased.connect(
            self.apply_brightness_slider
        )

        brightness_row.addWidget(
            brightness_text
        )

        brightness_row.addWidget(
            self.brightness_slider,
            1
        )

        brightness_row.addWidget(
            self.brightness_value
        )

        display_layout.addLayout(
            brightness_row
        )

        layout.addWidget(
            display_card
        )

        # =================================================
        # CONNECTIVITY
        # =================================================

        connection_card = self.create_card()

        connection_layout = QVBoxLayout(
            connection_card
        )

        connection_layout.setContentsMargins(
            22,
            18,
            22,
            18
        )

        connection_title = QLabel(
            "Connectivity"
        )

        connection_title.setObjectName(
            "cardTitle"
        )

        connection_layout.addWidget(
            connection_title
        )

        # WIFI

        wifi_row = QHBoxLayout()

        wifi_label = QLabel(
            "Wi-Fi"
        )

        wifi_label.setObjectName(
            "cardText"
        )

        wifi_on = QPushButton(
            "ON"
        )

        wifi_on.setObjectName(
            "controlButton"
        )

        wifi_off = QPushButton(
            "OFF"
        )

        wifi_off.setObjectName(
            "controlButton"
        )

        wifi_on.clicked.connect(
            lambda:
            self.run_system_action(
                set_wifi,
                True
            )
        )

        wifi_off.clicked.connect(
            lambda:
            self.run_system_action(
                set_wifi,
                False
            )
        )

        wifi_row.addWidget(
            wifi_label
        )

        wifi_row.addStretch()

        wifi_row.addWidget(
            wifi_on
        )

        wifi_row.addWidget(
            wifi_off
        )

        connection_layout.addLayout(
            wifi_row
        )

        # BLUETOOTH

        bluetooth_row = QHBoxLayout()

        bluetooth_label = QLabel(
            "Bluetooth"
        )

        bluetooth_label.setObjectName(
            "cardText"
        )

        bluetooth_on = QPushButton(
            "ON"
        )

        bluetooth_on.setObjectName(
            "controlButton"
        )

        bluetooth_off = QPushButton(
            "OFF"
        )

        bluetooth_off.setObjectName(
            "controlButton"
        )

        bluetooth_on.clicked.connect(
            lambda:
            self.run_system_action(
                set_bluetooth,
                True
            )
        )

        bluetooth_off.clicked.connect(
            lambda:
            self.run_system_action(
                set_bluetooth,
                False
            )
        )

        bluetooth_row.addWidget(
            bluetooth_label
        )

        bluetooth_row.addStretch()

        bluetooth_row.addWidget(
            bluetooth_on
        )

        bluetooth_row.addWidget(
            bluetooth_off
        )

        connection_layout.addLayout(
            bluetooth_row
        )

        layout.addWidget(
            connection_card
        )

        # =================================================
        # QUICK ACTIONS
        # =================================================

        action_card = self.create_card()

        action_layout = QVBoxLayout(
            action_card
        )

        action_layout.setContentsMargins(
            22,
            18,
            22,
            18
        )

        action_title = QLabel(
            "Quick Actions"
        )

        action_title.setObjectName(
            "cardTitle"
        )

        action_layout.addWidget(
            action_title
        )

        buttons_row = QHBoxLayout()

        screenshot_button = QPushButton(
            "Take Screenshot"
        )

        screenshot_button.setObjectName(
            "controlButton"
        )

        screenshot_button.clicked.connect(
            lambda:
            self.run_system_action(
                take_screenshot
            )
        )

        lock_button = QPushButton(
            "Lock PC"
        )

        lock_button.setObjectName(
            "controlButton"
        )

        lock_button.clicked.connect(
            lambda:
            self.run_system_action(
                lock_computer
            )
        )

        restart_button = QPushButton(
            "Restart"
        )

        restart_button.setObjectName(
            "dangerButton"
        )

        restart_button.clicked.connect(
            lambda:
            self.confirm_power_action(
                "restart"
            )
        )

        shutdown_button = QPushButton(
            "Shutdown"
        )

        shutdown_button.setObjectName(
            "dangerButton"
        )

        shutdown_button.clicked.connect(
            lambda:
            self.confirm_power_action(
                "shutdown"
            )
        )

        buttons_row.addWidget(
            screenshot_button
        )

        buttons_row.addWidget(
            lock_button
        )

        buttons_row.addStretch()

        buttons_row.addWidget(
            restart_button
        )

        buttons_row.addWidget(
            shutdown_button
        )

        action_layout.addLayout(
            buttons_row
        )

        layout.addWidget(
            action_card
        )

        self.system_status_label = QLabel(
            "Status: System controls ready"
        )

        self.system_status_label.setObjectName(
            "systemStatus"
        )

        layout.addWidget(
            self.system_status_label
        )

        layout.addStretch()

        return page

    # =====================================================
    # CREATE CARD
    # =====================================================

    def create_card(self):

        card = QFrame()

        card.setObjectName(
            "systemCard"
        )

        return card

    # =====================================================
    # SIMPLE PAGE
    # =====================================================

    def create_simple_page(
        self,
        title_text,
        description_text
    ):

        page = QFrame()

        page.setObjectName(
            "page"
        )

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            45,
            35,
            45,
            35
        )

        title = QLabel(
            title_text
        )

        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            description_text
        )

        description.setWordWrap(
            True
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            description
        )

        layout.addStretch()

        return page

    # =====================================================
    # COMMANDS PAGE TOGGLE
    # =====================================================

    def toggle_commands_page(self):

        current_index = (
            self.pages.currentIndex()
        )

        # If Commands page is already open,
        # go back to previous normal page.

        if (
            current_index
            == self.commands_page_index
        ):

            self.change_page(
                self.previous_page_index
            )

            return

        # Remember current page
        self.previous_page_index = (
            current_index
        )

        # Open Commands page
        self.pages.setCurrentIndex(
            self.commands_page_index
        )

        if hasattr(
            self,
            "top_page_title",
        ):
            self.top_page_title.setText(
                "Commands"
            )
            self.top_page_subtitle.setText(
                "Browse built-in and custom WizzArc commands"
            )

        self.commands_button.setText(
            "Back"
        )

        if hasattr(
            self,
            "commands_page",
        ):
            self.commands_page.setFocus()

        # No sidebar page should look active
        # while Commands is open.

        for button in self.menu_buttons:

            button.setProperty(
                "active",
                False
            )

            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )

    # =====================================================
    # AI ORB STATE
    # =====================================================

    def set_ai_state(
        self,
        state,
        title=None,
        message=None
    ):

        if hasattr(
            self,
            "ai_orb"
        ):
            self.ai_orb.set_state(
                state
            )

        if (
            title is not None
            and hasattr(
                self,
                "ai_status_title"
            )
        ):
            self.ai_status_title.setText(
                title
            )

        if (
            message is not None
            and hasattr(
                self,
                "ai_status_text"
            )
        ):
            self.ai_status_text.setText(
                message
            )



    # =====================================================
    # SUCCESS FEEDBACK
    # =====================================================

    def show_success_state(
        self,
        message,
        duration=1400
    ):

        self.set_ai_state(
            "success",
            "Done",
            str(message)
        )

        QTimer.singleShot(
            duration,
            lambda:
            self.set_ai_state(
                "idle",
                "WizzArc Ready",
                "Your desktop assistant is standing by."
            )
        )

    # =====================================================
    # IMPROVEMENT #6 - ALWAYS-ON MIC
    # =====================================================

    def toggle_always_on_mic(self):

        if self.always_on_mic_enabled:
            self.disable_always_on_mic()
        else:
            self.enable_always_on_mic()

    def enable_always_on_mic(self):

        if self.always_on_mic_enabled:
            return

        self.always_on_mic_enabled = True
        self.refresh_home_status_ui()

        self.home_mic_button.setText(
            "Mic ON"
        )

        self.status_label.setText(
            "Status: Wake listening..."
        )

        self.set_ai_state(
            "listening",
            "Wake Listening",
            f'Say "{self.wake_phrase}" to activate.'
        )

        self.start_wake_listener()

    def disable_always_on_mic(self):

        self.always_on_mic_enabled = False
        self.refresh_home_status_ui()

        if (
            self.home_wake_worker is not None
            and
            self.home_wake_worker.isRunning()
        ):
            self.home_wake_worker.stop()

        self.home_mic_button.setText(
            "Mic"
        )

        self.status_label.setText(
            "Status: Microphone off."
        )

        self.set_ai_state(
            "idle",
            "WizzArc Ready",
            "Microphone is off."
        )

    def start_wake_listener(self):

        if not self.always_on_mic_enabled:
            return

        if (
            self.home_voice_worker is not None
            and
            self.home_voice_worker.isRunning()
        ):
            return

        if (
            self.home_wake_worker is not None
            and
            self.home_wake_worker.isRunning()
        ):
            return

        wake_phrases = (
            (
                "wizzarc",
                "hey wizzarc",
                "ok wizzarc",
                "okay wizzarc",
            )
            if self.wake_phrase == "wizzarc"
            else (
                self.wake_phrase,
            )
        )

        self.home_wake_worker = WakeListenerWorker(
            self.voice_engine,
            wake_phrases=wake_phrases,
            parent=self,
        )

        self.home_wake_worker.wake_detected.connect(
            self.handle_wake_detected
        )

        self.home_wake_worker.status_changed.connect(
            self.handle_wake_status
        )

        self.home_wake_worker.error_occurred.connect(
            self.handle_wake_error
        )

        self.home_wake_worker.start()

    def handle_wake_detected(
        self,
        heard_text
    ):

        if not self.always_on_mic_enabled:
            return

        print(
            f"Wake detected: {heard_text}"
        )

        self.status_label.setText(
            "Status: Wake word detected."
        )

        self.set_ai_state(
            "listening",
            "I'm Listening",
            "Say your command."
        )

        # Give wake listener a moment to fully exit before
        # opening the microphone again for the actual command.
        QTimer.singleShot(
            250,
            self.start_home_voice
        )

    def handle_wake_status(
        self,
        status
    ):

        if not self.always_on_mic_enabled:
            return

        if status == "wake-listening":

            self.home_mic_button.setText(
                "Mic ON"
            )

            self.status_label.setText(
                "Status: Waiting for WizzArc..."
            )

            self.set_ai_state(
                "idle",
                "Wake Mode",
                'Say "WizzArc" when you need me.'
            )

    def handle_wake_error(
        self,
        error
    ):

        log_runtime_error(
            error,
            source="Wake Listener",
        )

        print(
            "Wake listener error:",
            error
        )

        if self.always_on_mic_enabled:

            self.status_label.setText(
                "Status: Wake listening had a problem. Retrying..."
            )

            self.set_ai_state(
                "idle",
                "Wake Mode",
                "Microphone listener is recovering."
            )

            QTimer.singleShot(
                1200,
                self.start_wake_listener
            )

    # =====================================================
    # HOME VOICE
    # =====================================================

    def start_home_voice(self):

        if (
            self.home_voice_worker
            is not None
            and
            self.home_voice_worker.isRunning()
        ):

            return

        self.status_label.setText(
            "Status: Listening..."
        )

        self.set_ai_state(
            "listening",
            "Listening...",
            "Speak your command."
        )

        self.home_mic_button.setText(
            "Command..."
        )

        # Keep the mic button usable so Always-On mode can
        # still be manually turned OFF.
        self.home_mic_button.setEnabled(
            True
        )

        self.home_voice_worker = VoiceWorker(
            self.voice_engine
        )

        self.home_voice_worker.result_ready.connect(
            self.handle_home_voice
        )

        self.home_voice_worker.error_occurred.connect(
            self.handle_home_voice_error
        )

        self.home_voice_worker.finished.connect(
            self.home_voice_finished
        )

        self.home_voice_worker.start()

    # =====================================================
    # HOME VOICE RESULT
    # =====================================================

    def handle_home_voice(
        self,
        command
    ):

        command = (
            command
            .strip()
        )

        if not command:

            self.status_label.setText(
                "Status: I couldn't hear that clearly."
            )

            return

        if command.startswith(
            "ERROR:"
        ):

            self.status_label.setText(
                f"Status: {command}"
            )

            return

        print(
            f"Voice heard: {command}"
        )

        log_activity(
            "voice_input",
            command,
            source="Home Voice",
            status="received",
        )

        self.set_ai_state(
            "thinking",
            "Understanding...",
            command
        )

        routed_command = (
            self.command_router.route(
                command
            )
        )

        print(
            f"Voice Router: "
            f"'{command}' -> '{routed_command}'"
        )

        self.command_input.setText(
            command
        )

        response = (
            self.get_voice_response(
                routed_command
            )
        )

        if response:

            self.set_ai_state(
                "speaking",
                "Responding...",
                response
            )

            self.speech_engine.speak(
                response
            )

        self.run_command()

        # run_command() handles the final visual state.

    # =====================================================
    # HOME VOICE ERROR
    # =====================================================

    def handle_home_voice_error(
        self,
        error
    ):

        log_runtime_error(
            error,
            source="Voice Input",
        )

        log_activity(
            "error",
            str(error),
            source="Voice Input",
            status="error",
        )

        self.status_label.setText(
            "Status: I couldn't use the microphone. Please try again."
        )

        self.set_ai_state(
            "idle",
            "WizzArc Ready",
            "Voice input failed safely."
        )

    # =====================================================
    # HOME VOICE FINISHED
    # =====================================================

    def home_voice_finished(self):

        self.home_mic_button.setEnabled(
            True
        )

        if self.always_on_mic_enabled:

            self.home_mic_button.setText(
                "Mic ON"
            )

            self.status_label.setText(
                "Status: Returning to wake mode..."
            )

            self.set_ai_state(
                "idle",
                "Wake Mode",
                'Say "WizzArc" when you need me.'
            )

            QTimer.singleShot(
                350,
                self.start_wake_listener
            )

        else:

            self.home_mic_button.setText(
                "Mic"
            )

            if hasattr(
                self,
                "ai_orb"
            ):
                self.ai_orb.set_state(
                    "idle"
                )

    # =====================================================
    # VOICE RESPONSES
    # =====================================================

    def get_voice_response(
        self,
        command
    ):

        command = (
            command
            .lower()
            .strip()
        )

        responses = {

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

            "volume up":
                "Increasing volume.",

            "volume down":
                "Decreasing volume.",

            "mute":
                "Muting audio.",

            "unmute":
                "Unmuting audio.",

            "brightness up":
                "Increasing brightness.",

            "brightness down":
                "Decreasing brightness.",

            "wifi on":
                "Turning Wi-Fi on.",

            "wifi off":
                "Turning Wi-Fi off.",

            "bluetooth on":
                "Turning Bluetooth on.",

            "bluetooth off":
                "Turning Bluetooth off.",

            "take screenshot":
                "Taking a screenshot.",

            "lock computer":
                "Locking your computer.",
        }

        # =================================================
        # CLOSE APP
        # =================================================

        if command.startswith(
            "close "
        ):

            app_name = command[
                len("close "):
            ].strip()

            if app_name:

                return (
                    f"Closing {app_name}."
                )

        # =================================================
        # DYNAMIC FOLDER
        # =================================================

        if command.startswith(
            "open folder "
        ):

            folder_name = command[
                len("open folder "):
            ].strip()

            return (
                f"Opening folder "
                f"{folder_name}."
            )

        # =================================================
        # DYNAMIC FILE
        # =================================================

        if command.startswith(
            "open file "
        ):

            file_name = command[
                len("open file "):
            ].strip()

            return (
                f"Opening file "
                f"{file_name}."
            )

        # =================================================
        # VOLUME VALUE
        # =================================================

        if command.startswith(
            "set volume to "
        ):

            value = command[
                len("set volume to "):
            ]

            return (
                f"Setting volume to "
                f"{value} percent."
            )

        # =================================================
        # BRIGHTNESS VALUE
        # =================================================

        if command.startswith(
            "set brightness to "
        ):

            value = command[
                len("set brightness to "):
            ]

            return (
                f"Setting brightness to "
                f"{value} percent."
            )

        return responses.get(
            command,
            "Okay."
        )

    # =====================================================
    # SYSTEM UI ACTION
    # =====================================================

    def run_system_action(
        self,
        function,
        *args
    ):

        result = function(
            *args
        )

        log_activity(
            "system_action",
            str(result),
            source="System Page",
            status="success",
        )

        self.system_status_label.setText(
            f"Status: {result}"
        )

    # =====================================================
    # VOLUME
    # =====================================================

    def apply_volume_slider(self):

        value = (
            self.volume_slider.value()
        )

        result = set_volume(
            value
        )

        log_activity(
            "system_action",
            str(result),
            source="Volume Slider",
            status="success",
            details={
                "value": value,
            },
        )

        self.system_status_label.setText(
            f"Status: {result}"
        )

    # =====================================================
    # BRIGHTNESS
    # =====================================================

    def apply_brightness_slider(self):

        value = (
            self.brightness_slider.value()
        )

        result = set_brightness(
            value
        )

        log_activity(
            "system_action",
            str(result),
            source="Brightness Slider",
            status="success",
            details={
                "value": value,
            },
        )

        self.system_status_label.setText(
            f"Status: {result}"
        )

    # =====================================================
    # POWER CONFIRMATION
    # =====================================================

    def confirm_power_action(
        self,
        action
    ):

        if action == "shutdown":

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
            QMessageBox.StandardButton.Cancel
        )

        if (
            answer
            == QMessageBox.StandardButton.Yes
        ):

            result = (
                perform_power_action(
                    action
                )
            )

        else:

            result = (
                f"{action.title()} cancelled."
            )

        log_activity(
            "power_action",
            str(result),
            source="System Page",
            status=(
                "cancelled"
                if "cancelled" in str(result).lower()
                else "success"
            ),
            details={
                "action": action,
            },
        )

        self.system_status_label.setText(
            f"Status: {result}"
        )

    # =====================================================
    # HOME SPEECH - NON-BLOCKING
    # =====================================================

    def speak_home_reply(
        self,
        text
    ):

        text = str(
            text
        ).strip()

        if not text:
            return

        if not self.speech_enabled:
            return

        # Avoid overlapping speech.
        if (
            self.home_speech_worker is not None
            and
            self.home_speech_worker.isRunning()
        ):
            return

        self.home_speech_worker = SpeechWorker(
            text,
            self,
        )

        self.home_speech_worker.error_occurred.connect(
            lambda error:
            print(
                "Home speech error:",
                error
            )
        )

        self.home_speech_worker.start()

    # =====================================================
    # HOME AI REQUEST - BACKGROUND THREAD
    # =====================================================

    def start_home_ai_request(
        self,
        original_command
    ):

        if (
            self.home_ai_worker is not None
            and
            self.home_ai_worker.isRunning()
        ):
            self.status_label.setText(
                "Status: WizzArc is still thinking..."
            )
            return

        self.pending_home_ai_text = str(
            original_command
        )

        log_activity(
            "ai_request",
            self.pending_home_ai_text,
            source="Home AI",
            status="started",
        )

        self.command_input.setEnabled(
            False
        )

        self.status_label.setText(
            "Status: Thinking..."
        )

        self.home_ai_worker = AIRequestWorker(
            self.ai_controller,
            original_command,
            self,
        )

        self.home_ai_worker.result_ready.connect(
            self.home_ai_result_ready
        )

        self.home_ai_worker.error_occurred.connect(
            self.home_ai_error
        )

        self.home_ai_worker.finished.connect(
            self.home_ai_finished
        )

        self.home_ai_worker.start()

    def execute_confirmed_dangerous_action(
        self,
        action,
    ):
        if action is None:
            return (
                "The requested action could not be verified."
            )

        kind = str(
            getattr(
                action,
                "kind",
                "",
            )
        ).strip().lower()

        command = str(
            getattr(
                action,
                "command",
                "",
            )
        ).strip()

        if kind in {
            "shutdown",
            "restart",
        }:
            return perform_power_action(
                kind
            )

        if kind == "delete":
            delete_target, delete_error = (
                prepare_delete(
                    command
                )
            )

            if delete_error:
                return delete_error

            if delete_target is None:
                return (
                    "I couldn't find the item to delete."
                )

            return delete_item(
                delete_target
            )

        return (
            "This action is not approved for "
            "confirmed execution."
        )

    def handle_ai_confirmation(
        self,
        ai_result,
    ):
        action = getattr(
            ai_result,
            "dangerous_action",
            None,
        )

        if action is None:
            self.status_label.setText(
                "Status: Confirmation data was missing."
            )
            return

        title = (
            getattr(
                action,
                "title",
                "",
            )
            or "Confirm Action"
        )

        message = (
            getattr(
                action,
                "message",
                "",
            )
            or "Do you want to continue with this action?"
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
            try:
                result = (
                    self.execute_confirmed_dangerous_action(
                        action
                    )
                )

                log_activity(
                    "security_confirmation",
                    str(result),
                    source="AI Safety",
                    status="confirmed",
                    details={
                        "command": getattr(
                            action,
                            "command",
                            "",
                        ),
                        "kind": getattr(
                            action,
                            "kind",
                            "",
                        ),
                    },
                )

                self.status_label.setText(
                    f"Status: {result}"
                )

                self.set_ai_state(
                    "success",
                    "Confirmed",
                    str(result),
                )

                self.speak_home_reply(
                    str(result)
                )

            except Exception as error:
                log_runtime_error(
                    error,
                    source="AI Confirmed Action",
                )

                log_activity(
                    "error",
                    str(error),
                    source="AI Safety",
                    status="error",
                )

                self.status_label.setText(
                    "Status: The confirmed action failed safely."
                )

                self.set_ai_state(
                    "idle",
                    "WizzArc Ready",
                    "The action was not completed.",
                )

        else:
            cancelled = (
                f"{getattr(action, 'kind', 'Action').title()} "
                "cancelled."
            )

            log_activity(
                "security_confirmation",
                cancelled,
                source="AI Safety",
                status="cancelled",
                details={
                    "command": getattr(
                        action,
                        "command",
                        "",
                    ),
                },
            )

            self.status_label.setText(
                f"Status: {cancelled}"
            )

            self.set_ai_state(
                "idle",
                "WizzArc Ready",
                cancelled,
            )

        self.command_input.clear()

    def home_ai_result_ready(
        self,
        ai_result
    ):

        if (
            getattr(
                ai_result,
                "confirmation_required",
                False,
            )
            or getattr(
                ai_result,
                "route",
                "",
            ) == "confirmation"
        ):
            self.handle_ai_confirmation(
                ai_result
            )
            return

        if ai_result.success:

            reply = (
                ai_result.text
                or "Done."
            )

            self.status_label.setText(
                f"Status: {reply}"
            )

            log_activity(
                "ai_result",
                reply,
                source="Home AI",
                status="success",
                details={
                    "route": str(
                        getattr(
                            ai_result,
                            "route",
                            "",
                        )
                    ),
                    "request": self.pending_home_ai_text,
                },
            )

            # Improvement #6 foundation:
            # Home AI replies are always shown and spoken.
            self.speak_home_reply(
                reply
            )

            self.command_input.clear()

            if (
                ai_result.route
                in {
                    "action",
                    "multi_action",
                }
            ):
                self.show_success_state(
                    reply
                )

            else:
                self.set_ai_state(
                    "idle",
                    "WizzArc Ready",
                    reply
                )

            return

        technical_error = (
            ai_result.error
            or "AI request returned an unsuccessful result."
        )

        log_runtime_error(
            technical_error,
            source="AI Controller Result",
        )

        log_activity(
            "error",
            str(technical_error),
            source="AI Controller Result",
            status="error",
            details={
                "request": self.pending_home_ai_text,
            },
        )

        error_text = (
            "I couldn't complete that request. Please try again."
        )

        self.status_label.setText(
            f"Status: {error_text}"
        )

        self.set_ai_state(
            "idle",
            "WizzArc Ready",
            error_text
        )

    def home_ai_error(
        self,
        error
    ):

        log_runtime_error(
            error,
            source="AI Worker",
        )

        log_activity(
            "error",
            str(error),
            source="AI Worker",
            status="error",
            details={
                "request": self.pending_home_ai_text,
            },
        )

        self.status_label.setText(
            "Status: AI is temporarily unavailable. Please try again."
        )

        self.set_ai_state(
            "idle",
            "WizzArc Ready",
            "AI request failed safely."
        )

    def home_ai_finished(
        self
    ):

        self.command_input.setEnabled(
            True
        )

        self.command_input.setFocus()

    # =====================================================
    # HOME COMMAND
    # =====================================================

    def run_command(self):

        original_command = (
            self.command_input
            .text()
            .strip()
        )

        if not original_command:

            self.status_label.setText(
                "Status: Please enter a command."
            )

            return

        log_activity(
            "command",
            original_command,
            source="Home Command",
            status="received",
        )

        self.set_ai_state(
            "thinking",
            "Working...",
            original_command
        )

        # =================================================
        # HOME ROUTING
        # =================================================
        #
        # Exact registered commands keep the legacy Home
        # behavior (Files page, special UI actions, etc.).
        # Everything else goes to Phase 8 AIController first,
        # so Home can also handle normal conversation,
        # memory, natural actions and contextual follow-ups.

        registered = resolve_registered_command(
            original_command
        )

        if registered is None:

            if self.ai_controller is not None:

                self.set_ai_state(
                    "thinking",
                    "Thinking...",
                    original_command
                )

                self.start_home_ai_request(
                    original_command
                )

                return

            log_runtime_error(
                self.ai_backend_error
                or "AI controller is unavailable.",
                source="AI Startup",
            )

            log_activity(
                "error",
                self.ai_backend_error
                or "AI controller is unavailable.",
                source="AI Startup",
                status="error",
                details={
                    "request": original_command,
                },
            )

            self.status_label.setText(
                "Status: AI is unavailable right now."
            )

            self.command_input.clear()

            self.set_ai_state(
                "idle",
                "WizzArc Ready",
                "AI is unavailable. Other desktop controls can still work."
            )

            return

        command = registered[
            "command"
        ]

        print(
            f"Registered Home Command: "
            f"'{original_command}' "
            f"-> '{command}'"
        )

        # =================================================
        # SHOW DRIVES / FILES / FOLDERS IN FILES PAGE
        # IMPROVEMENT #5
        # =================================================

        # -------------------------------------------------
        # SHOW ALL DRIVES
        # -------------------------------------------------

        if command == "show all drives":

            drives = get_available_drives()

            self.files_page.show_items(
                "This PC",
                drives
            )

            self.change_page(2)

            count = len(drives)

            result = (
                f"Showing {count} "
                f"drive{'s' if count != 1 else ''}."
            )

            self.status_label.setText(
                f"Status: {result}"
            )

            self.show_success_state(
                result
            )

            self.command_input.clear()
            return

        # -------------------------------------------------
        # DETECT LIST MODE
        # -------------------------------------------------

        list_mode = None
        location = None

        if command.startswith(
            "show all folders in "
        ):

            list_mode = "folders"
            location = command[
                len("show all folders in "):
            ].strip()

        elif command.startswith(
            "show all files in "
        ):

            list_mode = "files"
            location = command[
                len("show all files in "):
            ].strip()

        elif command.startswith(
            "show everything in "
        ):

            list_mode = "all"
            location = command[
                len("show everything in "):
            ].strip()

        elif command.startswith(
            "show all items in "
        ):

            list_mode = "all"
            location = command[
                len("show all items in "):
            ].strip()

        if list_mode and location:

            # =============================================
            # DRIVE LOCATION
            # Example: c drive / d drive
            # =============================================

            if location.endswith(
                " drive"
            ):

                drive_name = location[
                    :-len(" drive")
                ].strip()

                items, error = list_drive_items(
                    drive_name,
                    folders_only=(list_mode == "folders"),
                    files_only=(list_mode == "files")
                )

                display_location = (
                    f"{drive_name.upper()} Drive"
                )

            # =============================================
            # KNOWN WINDOWS LOCATION
            # Documents / Downloads / Pictures etc.
            # =============================================

            else:

                items, error = list_items(
                    location,
                    folders_only=(list_mode == "folders"),
                    files_only=(list_mode == "files")
                )

                display_location = location

            if error:

                self.status_label.setText(
                    f"Status: {error}"
                )

                self.set_ai_state(
                    "idle",
                    "WizzArc Ready",
                    error
                )

            else:

                self.files_page.show_items(
                    display_location,
                    items
                )

                self.change_page(2)

                count = len(items)

                result = (
                    f"Showing {count} "
                    f"item{'s' if count != 1 else ''} "
                    f"from {display_location}."
                )

                self.status_label.setText(
                    f"Status: {result}"
                )

                self.show_success_state(
                    result
                )

            self.command_input.clear()
            return

        # =================================================
        # DELETE
        # =================================================

        delete_target, delete_error = (
            prepare_delete(
                command
            )
        )

        if delete_error:

            self.status_label.setText(
                f"Status: {delete_error}"
            )

            self.command_input.clear()

            return

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
                QMessageBox.StandardButton.Cancel
            )

            if (
                answer
                == QMessageBox.StandardButton.Yes
            ):

                result = delete_item(
                    delete_target
                )

            else:

                result = (
                    "Delete cancelled."
                )

            self.status_label.setText(
                f"Status: {result}"
            )

            log_activity(
                "desktop_action",
                str(result),
                source="Delete",
                status=(
                    "cancelled"
                    if "cancelled" in str(result).lower()
                    else "success"
                ),
                details={
                    "command": original_command,
                },
            )

            self.command_input.clear()

            return

        # =================================================
        # POWER
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
                QMessageBox.StandardButton.Cancel
            )

            if (
                answer
                == QMessageBox.StandardButton.Yes
            ):

                result = (
                    perform_power_action(
                        power_action
                    )
                )

            else:

                result = (
                    f"{power_action.title()} "
                    "cancelled."
                )

            self.status_label.setText(
                f"Status: {result}"
            )

            log_activity(
                "power_action",
                str(result),
                source="Home Command",
                status=(
                    "cancelled"
                    if "cancelled" in str(result).lower()
                    else "success"
                ),
                details={
                    "command": original_command,
                },
            )

            self.command_input.clear()

            return

        # =================================================
        # SYSTEM
        # =================================================

        system_result = (
            execute_system_command(
                command
            )
        )

        if system_result is not None:

            self.status_label.setText(
                f"Status: {system_result}"
            )

            log_activity(
                "system_action",
                str(system_result),
                source="Home Command",
                status="success",
                details={
                    "command": original_command,
                },
            )

            self.command_input.clear()

            return

        # =================================================
        # DESKTOP
        # =================================================

        result = execute_command(
            command
        )

        self.status_label.setText(
            f"Status: {result}"
        )

        log_activity(
            "desktop_action",
            str(result),
            source="Home Command",
            status="success",
            details={
                "command": original_command,
            },
        )

        self.command_input.clear()

        self.show_success_state(
            result
        )

    # =====================================================
    # PHASE 9.5 - APPLY SAVED SETTINGS
    # =====================================================

    def apply_saved_settings(
        self,
        settings,
    ):
        old_model = getattr(
            self,
            "ai_model",
            "qwen3:4b",
        )

        self.user_settings = dict(
            settings
        )

        self.wake_phrase = str(
            settings.get(
                "wake_phrase",
                "wizzarc",
            )
        ).strip().lower() or "wizzarc"

        self.speech_enabled = bool(
            settings.get(
                "speech_enabled",
                True,
            )
        )

        self.always_on_mic_default = bool(
            settings.get(
                "always_on_mic_default",
                False,
            )
        )

        self.start_minimized = bool(
            settings.get(
                "start_minimized",
                False,
            )
        )

        self.ai_model = str(
            settings.get(
                "ai_model",
                old_model,
            )
        ).strip() or old_model

        log_activity(
            "settings",
            "User preferences saved.",
            source="Settings",
            status="success",
        )

        # A new wake phrase should be used by the next wake-listener
        # cycle. Restart the current wake listener when possible.
        if (
            self.always_on_mic_enabled
            and self.home_wake_worker is not None
            and self.home_wake_worker.isRunning()
        ):
            self.home_wake_worker.stop()
            QTimer.singleShot(
                500,
                self.start_wake_listener,
            )

        # Reconnect AI only if the model preference actually changed.
        if self.ai_model != old_model:
            try:
                connect_ollama(
                    AI_ENGINE,
                    model=self.ai_model,
                )

                self.ai_controller = AIController(
                    AI_ENGINE,
                    execute_wizzarc_command,
                )

                self.ai_backend_error = None

                self.set_ai_state(
                    "success",
                    "AI Model Updated",
                    f"Using {self.ai_model}.",
                )

            except Exception as error:
                self.ai_backend_error = str(
                    error
                )

                log_runtime_error(
                    error,
                    source="Settings AI model change",
                )

                self.set_ai_state(
                    "error",
                    "AI Model Error",
                    "The selected Ollama model could not be loaded.",
                )

        self.refresh_home_status_ui()

    # =====================================================
    # PHASE 9.3 - SAFE SHUTDOWN
    # =====================================================

    def _shutdown_worker(
        self,
        worker,
        name,
        wait_ms=1800,
    ):
        """
        Stop one QThread-like worker without letting app shutdown
        crash because a thread is still running.
        """

        if worker is None:
            return True

        try:
            if not worker.isRunning():
                return True

            # Custom cooperative stop, used by WakeListenerWorker.
            stop_method = getattr(
                worker,
                "stop",
                None,
            )

            if callable(
                stop_method
            ):
                try:
                    stop_method()
                except Exception as error:
                    log_runtime_error(
                        error,
                        source=(
                            f"Shutdown {name} stop()"
                        ),
                    )

            # Standard Qt interruption request.
            try:
                worker.requestInterruption()
            except Exception:
                pass

            # quit() helps workers that run an event loop.
            try:
                worker.quit()
            except Exception:
                pass

            if worker.wait(
                wait_ms
            ):
                return True

            # Final fallback. We only use terminate during application
            # shutdown after giving the worker time to exit normally.
            log_runtime_error(
                (
                    f"{name} did not stop within "
                    f"{wait_ms} ms; forcing shutdown."
                ),
                source="Safe Shutdown",
            )

            try:
                worker.terminate()
                worker.wait(
                    700
                )
            except Exception as error:
                log_runtime_error(
                    error,
                    source=(
                        f"Shutdown {name} terminate"
                    ),
                )

            return not worker.isRunning()

        except Exception as error:

            log_runtime_error(
                error,
                source=(
                    f"Shutdown {name}"
                ),
            )

            return False

    def shutdown_background_workers(
        self,
    ):
        """
        Stop Home + Assistant-page background workers.
        """

        # Prevent wake mode from automatically restarting while closing.
        self.always_on_mic_enabled = False

        workers = [
            (
                "Home Wake Listener",
                getattr(
                    self,
                    "home_wake_worker",
                    None,
                ),
            ),
            (
                "Home Voice Worker",
                getattr(
                    self,
                    "home_voice_worker",
                    None,
                ),
            ),
            (
                "Home AI Worker",
                getattr(
                    self,
                    "home_ai_worker",
                    None,
                ),
            ),
            (
                "Home Speech Worker",
                getattr(
                    self,
                    "home_speech_worker",
                    None,
                ),
            ),
        ]

        assistant_page = getattr(
            self,
            "assistant_page",
            None,
        )

        if assistant_page is not None:

            workers.extend(
                [
                    (
                        "Assistant Voice Worker",
                        getattr(
                            assistant_page,
                            "voice_worker",
                            None,
                        ),
                    ),
                    (
                        "Assistant AI Worker",
                        getattr(
                            assistant_page,
                            "ai_worker",
                            None,
                        ),
                    ),
                    (
                        "Assistant Speech Worker",
                        getattr(
                            assistant_page,
                            "speech_worker",
                            None,
                        ),
                    ),
                ]
            )

        all_stopped = True

        for name, worker in workers:

            stopped = self._shutdown_worker(
                worker,
                name,
            )

            if not stopped:
                all_stopped = False

        return all_stopped

    def closeEvent(
        self,
        event,
    ):
        """
        Qt window close hook.
        """

        try:
            all_stopped = (
                self.shutdown_background_workers()
            )

            if all_stopped:
                print(
                    "WizzArc background workers stopped safely."
                )
            else:
                print(
                    "WizzArc closed with one or more forced worker shutdowns."
                )

        except Exception as error:

            log_runtime_error(
                error,
                source="WizzArc closeEvent",
            )

        event.accept()

    # =====================================================
    # PHASE 9.8 - FINAL PAGE POLISH
    # =====================================================

    def apply_page_focus_state(
        self,
        index,
    ):
        if (
            index == 0
            and hasattr(
                self,
                "command_input",
            )
        ):
            self.command_input.setFocus()

        current_widget = (
            self.pages.widget(index)
            if (
                hasattr(self, "pages")
                and 0 <= index < self.pages.count()
            )
            else None
        )

        if (
            current_widget is not None
            and index != 7
            and hasattr(
                current_widget,
                "refresh",
            )
            and callable(
                current_widget.refresh
            )
        ):
            try:
                current_widget.refresh()
            except Exception:
                pass

    # =====================================================
    # CHANGE PAGE
    # =====================================================

    def change_page(
        self,
        index
    ):

        self.pages.setCurrentIndex(
            index
        )

        self.apply_page_focus_state(
            index
        )

        if (
            hasattr(
                self,
                "top_page_title",
            )
            and 0 <= index < len(
                getattr(
                    self,
                    "page_names",
                    [],
                )
            )
        ):
            self.top_page_title.setText(
                self.page_names[index]
            )

            self.top_page_subtitle.setText(
                self.page_subtitles[index]
            )

        if (
            index == 7
            and hasattr(
                self,
                "activity_page",
            )
        ):
            self.activity_page.refresh()

        self.previous_page_index = (
            index
        )

        self.commands_button.setText(
            "Commands"
        )

        for i, button in enumerate(
            self.menu_buttons
        ):

            button.setProperty(
                "active",
                i == index
            )

            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )


# =========================================================
# START WIZZARC
# =========================================================

# Phase 9.2 - global crash/error logging
error_log_path = install_global_error_handlers()

print(
    f"WizzArc error logging ready: {error_log_path}"
)

app = QApplication(
    sys.argv
)

if ICON_PATH.exists():

    app.setWindowIcon(
        QIcon(str(ICON_PATH))
    )

window = WizzArc()

# =========================================================
# RESTORE SAVED AUTOMATIONS
# =========================================================

restore_result = restore_saved_automations(
    execute_command
)

print(
    f"Automation Restore: "
    f"{restore_result}"
)

if window.start_minimized:
    window.showMinimized()
else:
    window.show()

sys.exit(
    app.exec()
)