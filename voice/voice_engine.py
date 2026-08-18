import re
import tempfile
import wave
import time
from pathlib import Path
from collections import deque
from difflib import SequenceMatcher

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


# =========================================================
# SETTINGS
# =========================================================

SAMPLE_RATE = 16000

# Working microphone
MIC_DEVICE = 2

# Multilingual model
WHISPER_MODEL = "base"

BLOCK_DURATION = 0.1
BLOCK_SIZE = int(
    SAMPLE_RATE * BLOCK_DURATION
)

CALIBRATION_SECONDS = 1.0

MIN_THRESHOLD = 120
THRESHOLD_MULTIPLIER = 2.2

PRE_BUFFER_SECONDS = 0.5

SILENCE_SECONDS = 1.5

WAIT_FOR_SPEECH_SECONDS = 7

MAX_RECORD_SECONDS = 15

MIN_SPEECH_SECONDS = 0.35

FUZZY_THRESHOLD = 0.78


# =========================================================
# FIXED COMMANDS
# =========================================================

VOICE_COMMANDS = [
    "open chrome",
    "open edge",
    "open calculator",
    "open notepad",
    "open paint",
    "open vscode",
    "open visual studio code",

    "open downloads",
    "open documents",
    "open desktop",
    "open pictures",
    "open music",
    "open videos",

    "volume up",
    "volume down",
    "mute",
    "unmute",

    "brightness up",
    "brightness down",

    "wifi on",
    "wifi off",

    "bluetooth on",
    "bluetooth off",

    "take screenshot",
    "lock computer",

    "shutdown",
    "restart",
]


# =========================================================
# HINGLISH ALIASES
# =========================================================

COMMAND_ALIASES = {

    # Apps
    "chrome kholo":
        "open chrome",

    "chrome khol":
        "open chrome",

    "chrome open karo":
        "open chrome",

    "edge kholo":
        "open edge",

    "edge open karo":
        "open edge",

    "calculator kholo":
        "open calculator",

    "calculator open karo":
        "open calculator",

    "notepad kholo":
        "open notepad",

    "notepad open karo":
        "open notepad",

    "vs code kholo":
        "open vscode",

    "vscode kholo":
        "open vscode",

    "visual studio code kholo":
        "open visual studio code",

    # Known folders
    "downloads kholo":
        "open downloads",

    "documents kholo":
        "open documents",

    "desktop kholo":
        "open desktop",

    "pictures kholo":
        "open pictures",

    "videos kholo":
        "open videos",

    "music kholo":
        "open music",

    # Volume
    "volume badhao":
        "volume up",

    "volume badao":
        "volume up",

    "awaz badhao":
        "volume up",

    "awaaz badhao":
        "volume up",

    "volume kam karo":
        "volume down",

    "awaz kam karo":
        "volume down",

    "awaaz kam karo":
        "volume down",

    "mute karo":
        "mute",

    "unmute karo":
        "unmute",

    # Brightness
    "brightness badhao":
        "brightness up",

    "brightness badao":
        "brightness up",

    "brightness kam karo":
        "brightness down",

    # Wi-Fi
    "wifi chalu karo":
        "wifi on",

    "wifi on karo":
        "wifi on",

    "wifi band karo":
        "wifi off",

    "wifi off karo":
        "wifi off",

    # Bluetooth
    "bluetooth chalu karo":
        "bluetooth on",

    "bluetooth on karo":
        "bluetooth on",

    "bluetooth band karo":
        "bluetooth off",

    "bluetooth off karo":
        "bluetooth off",

    # Other
    "screenshot lo":
        "take screenshot",

    "screenshot le lo":
        "take screenshot",

    "computer lock karo":
        "lock computer",

    "pc lock karo":
        "lock computer",
}


class VoiceEngine:

    def __init__(self):

        print(
            "Loading WizzArc voice model..."
        )

        self.model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8"
        )

        print(
            "Voice model ready."
        )

    # =====================================================
    # AUDIO LEVEL
    # =====================================================

    def get_audio_level(
        self,
        audio
    ):

        if audio.size == 0:
            return 0.0

        audio_float = audio.astype(
            np.float32
        )

        return float(
            np.sqrt(
                np.mean(
                    audio_float ** 2
                )
            )
        )

    # =====================================================
    # MICROPHONE CALIBRATION
    # =====================================================

    def calibrate_microphone(
        self,
        stream
    ):

        print(
            "Calibrating microphone... stay quiet."
        )

        levels = []

        blocks = max(
            1,
            int(
                CALIBRATION_SECONDS
                / BLOCK_DURATION
            )
        )

        for _ in range(blocks):

            data, overflowed = stream.read(
                BLOCK_SIZE
            )

            audio_array = np.frombuffer(
                data,
                dtype=np.int16
            )

            level = self.get_audio_level(
                audio_array
            )

            levels.append(
                level
            )

        if not levels:
            return MIN_THRESHOLD

        noise_level = float(
            np.median(
                levels
            )
        )

        threshold = max(
            MIN_THRESHOLD,
            noise_level
            * THRESHOLD_MULTIPLIER
        )

        print(
            f"Background level: "
            f"{int(noise_level)}"
        )

        print(
            f"Voice threshold: "
            f"{int(threshold)}"
        )

        return threshold

    # =====================================================
    # SMART RECORDING
    # =====================================================

    def record_audio(self):

        recorded_blocks = []

        speech_started = False
        speech_start_time = None
        last_voice_time = None

        pre_buffer_size = max(
            1,
            int(
                PRE_BUFFER_SECONDS
                / BLOCK_DURATION
            )
        )

        pre_buffer = deque(
            maxlen=pre_buffer_size
        )

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            device=MIC_DEVICE,
            dtype="int16",
            channels=1,
        ) as stream:

            threshold = (
                self.calibrate_microphone(
                    stream
                )
            )

            print(
                "Listening..."
            )

            listening_start = (
                time.monotonic()
            )

            while True:

                data, overflowed = (
                    stream.read(
                        BLOCK_SIZE
                    )
                )

                data_bytes = bytes(
                    data
                )

                audio_array = (
                    np.frombuffer(
                        data,
                        dtype=np.int16
                    )
                )

                level = (
                    self.get_audio_level(
                        audio_array
                    )
                )

                now = time.monotonic()

                print(
                    f"\rMic: "
                    f"{int(level):4d} | "
                    f"Threshold: "
                    f"{int(threshold):4d}",
                    end="",
                    flush=True
                )

                # =========================================
                # WAIT FOR SPEECH
                # =========================================

                if not speech_started:

                    pre_buffer.append(
                        data_bytes
                    )

                    if level >= threshold:

                        speech_started = True

                        speech_start_time = now
                        last_voice_time = now

                        recorded_blocks.extend(
                            list(
                                pre_buffer
                            )
                        )

                        print(
                            "\nSpeech detected..."
                        )

                    elif (
                        now - listening_start
                        >= WAIT_FOR_SPEECH_SECONDS
                    ):

                        print(
                            "\nNo speech detected."
                        )

                        return None

                # =========================================
                # RECORD SPEECH
                # =========================================

                else:

                    recorded_blocks.append(
                        data_bytes
                    )

                    if level >= threshold:

                        last_voice_time = now

                    if (
                        last_voice_time
                        is not None
                        and
                        now - last_voice_time
                        >= SILENCE_SECONDS
                    ):

                        print(
                            "\nSpeech finished."
                        )

                        break

                    if (
                        speech_start_time
                        is not None
                        and
                        now - speech_start_time
                        >= MAX_RECORD_SECONDS
                    ):

                        print(
                            "\nMaximum recording time reached."
                        )

                        break

        if (
            speech_start_time is None
            or not recorded_blocks
        ):

            return None

        speech_duration = (
            time.monotonic()
            - speech_start_time
        )

        if (
            speech_duration
            < MIN_SPEECH_SECONDS
        ):

            print(
                "Speech was too short. Ignoring."
            )

            return None

        return b"".join(
            recorded_blocks
        )

    # =====================================================
    # SAVE WAV
    # =====================================================

    def save_temp_audio(
        self,
        audio_bytes
    ):

        temp_file = (
            tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            )
        )

        temp_path = Path(
            temp_file.name
        )

        temp_file.close()

        with wave.open(
            str(temp_path),
            "wb"
        ) as wav_file:

            wav_file.setnchannels(
                1
            )

            wav_file.setsampwidth(
                2
            )

            wav_file.setframerate(
                SAMPLE_RATE
            )

            wav_file.writeframes(
                audio_bytes
            )

        return temp_path

    # =====================================================
    # NORMALIZE TEXT
    # =====================================================

    def normalize_text(
        self,
        text
    ):

        text = (
            str(text)
            .lower()
            .strip()
        )

        text = re.sub(
            r"[.!?,;:]+",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =====================================================
    # FIX COMMON TRANSCRIPTION VARIANTS
    # =====================================================

    def fix_common_words(
        self,
        text
    ):

        replacements = {
            "google crom":
                "google chrome",

            "google crome":
                "google chrome",

            "open crome":
                "open chrome",

            "open crom":
                "open chrome",

            "wi fi":
                "wifi",

            "blue tooth":
                "bluetooth",

            "vs code":
                "vscode",

            "visual studio":
                "visual studio code",
        }

        for old, new in replacements.items():

            text = text.replace(
                old,
                new
            )

        return text

    # =====================================================
    # DYNAMIC COMMAND DETECTION
    # =====================================================

    def detect_dynamic_command(
        self,
        text
    ):

        # -------------------------------------------------
        # OPEN FOLDER
        # -------------------------------------------------

        patterns = [
            r"^open folder\s+(.+)$",
            r"^open the folder\s+(.+)$",
            r"^folder\s+(.+)\s+open$",
            r"^(.+)\s+folder\s+kholo$",
            r"^(.+)\s+folder\s+khol do$",
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                text
            )

            if match:

                name = (
                    match.group(1)
                    .strip()
                )

                if name:

                    return (
                        f"open folder {name}"
                    )

        # -------------------------------------------------
        # OPEN FILE
        # -------------------------------------------------

        patterns = [
            r"^open file\s+(.+)$",
            r"^open the file\s+(.+)$",
            r"^file\s+(.+)\s+open$",
            r"^(.+)\s+file\s+kholo$",
            r"^(.+)\s+file\s+khol do$",
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                text
            )

            if match:

                name = (
                    match.group(1)
                    .strip()
                )

                if name:

                    return (
                        f"open file {name}"
                    )

        # -------------------------------------------------
        # FIND / SEARCH FILE OR FOLDER
        # -------------------------------------------------

        patterns = [
            r"^find folder\s+(.+)$",
            r"^search folder\s+(.+)$",
            r"^find file\s+(.+)$",
            r"^search file\s+(.+)$",
            r"^find\s+(.+)$",
            r"^search\s+(.+)$",
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                text
            )

            if match:

                name = (
                    match.group(1)
                    .strip()
                )

                if name:

                    return (
                        f"find {name}"
                    )

        # -------------------------------------------------
        # CREATE FOLDER
        # -------------------------------------------------

        match = re.match(
            r"^create folder\s+(.+)$",
            text
        )

        if match:

            name = (
                match.group(1)
                .strip()
            )

            if name:

                return (
                    f"create folder {name}"
                )

        # -------------------------------------------------
        # RENAME FILE / FOLDER
        # -------------------------------------------------

        if text.startswith(
            "rename folder "
        ):

            return text

        if text.startswith(
            "rename file "
        ):

            return text

        # -------------------------------------------------
        # MOVE / COPY
        # -------------------------------------------------

        for prefix in [
            "move folder ",
            "move file ",
            "copy folder ",
            "copy file ",
        ]:

            if text.startswith(
                prefix
            ):

                return text

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        if text.startswith(
            "delete folder "
        ):

            return text

        if text.startswith(
            "delete file "
        ):

            return text

        # -------------------------------------------------
        # CLOSE APP
        # -------------------------------------------------

        if text.startswith(
            "close "
        ):

            return text

        # -------------------------------------------------
        # APP RUNNING CHECK
        # -------------------------------------------------

        if (
            text.startswith(
                "is "
            )
            and text.endswith(
                " running"
            )
        ):

            return text

        return None

    # =====================================================
    # COMMAND MATCHING
    # =====================================================

    def match_command(
        self,
        raw_text
    ):

        text = self.normalize_text(
            raw_text
        )

        text = self.fix_common_words(
            text
        )

        print(
            f"Raw speech: {text}"
        )

        if not text:
            return ""

        # =================================================
        # DYNAMIC COMMAND FIRST
        # =================================================

        dynamic_command = (
            self.detect_dynamic_command(
                text
            )
        )

        if dynamic_command:

            print(
                "Dynamic command: "
                f"{dynamic_command}"
            )

            return dynamic_command

        # =================================================
        # HINGLISH ALIASES
        # =================================================

        for alias, command in (
            COMMAND_ALIASES.items()
        ):

            if (
                text == alias
                or alias in text
            ):

                print(
                    "Hinglish command: "
                    f"{alias} -> {command}"
                )

                return command

        # =================================================
        # EXACT FIXED COMMAND
        # =================================================

        for command in VOICE_COMMANDS:

            if text == command:

                print(
                    f"Exact match: {command}"
                )

                return command

        # =================================================
        # COMMAND INSIDE TRANSCRIPTION
        # =================================================

        for command in VOICE_COMMANDS:

            if command in text:

                print(
                    f"Command found: {command}"
                )

                return command

        # =================================================
        # FUZZY FIXED COMMAND
        # =================================================

        best_command = None
        best_score = 0.0

        for command in VOICE_COMMANDS:

            score = SequenceMatcher(
                None,
                text,
                command
            ).ratio()

            if score > best_score:

                best_score = score
                best_command = command

        print(
            f"Closest fixed command: "
            f"{best_command} "
            f"({best_score:.2f})"
        )

        if (
            best_command
            and
            best_score >= FUZZY_THRESHOLD
        ):

            print(
                f"Accepted: {best_command}"
            )

            return best_command

        # =================================================
        # LAST SAFE PASS-THROUGH
        # =================================================
        #
        # If Whisper clearly heard an action verb,
        # preserve it for CommandRouter/DesktopActions.
        #
        # This is what lets arbitrary names survive.

        safe_action_prefixes = [
            "open ",
            "find ",
            "search ",
            "create ",
            "rename ",
            "move ",
            "copy ",
            "delete ",
            "close ",
            "launch ",
            "start ",
        ]

        for prefix in safe_action_prefixes:

            if text.startswith(
                prefix
            ):

                print(
                    "Dynamic speech preserved: "
                    f"{text}"
                )

                return text

        print(
            "No reliable command match."
        )

        return ""

    # =====================================================
    # WHISPER TRANSCRIPTION
    # =====================================================

    def transcribe_audio(
        self,
        temp_path
    ):

        print(
            "Understanding..."
        )

        segments, info = (
            self.model.transcribe(
                str(temp_path),

                beam_size=5,

                vad_filter=True,

                condition_on_previous_text=False,

                initial_prompt=(
                    "Windows desktop assistant command. "
                    "Commands may contain custom application, "
                    "file or folder names. "
                    "Examples: "
                    "Open Chrome. "
                    "Open Calculator. "
                    "Open folder CSS. "
                    "Open folder Python Projects. "
                    "Open file notes.txt. "
                    "Find folder College. "
                    "Find file report.pdf. "
                    "Create folder Test Project. "
                    "Close Discord. "
                    "Set volume to 50. "
                    "Set brightness to 70. "
                    "WiFi off. "
                    "Bluetooth on. "
                    "Take screenshot."
                )
            )
        )

        parts = []

        for segment in segments:

            text = (
                segment.text
                .strip()
            )

            if text:

                parts.append(
                    text
                )

        raw_text = " ".join(
            parts
        )

        return self.match_command(
            raw_text
        )

    # =====================================================
    # MAIN LISTEN
    # =====================================================

    def listen_once(self):

        temp_path = None

        try:

            audio = self.record_audio()

            if audio is None:

                return ""

            temp_path = (
                self.save_temp_audio(
                    audio
                )
            )

            command = (
                self.transcribe_audio(
                    temp_path
                )
            )

            if command:

                print(
                    f"Heard: {command}"
                )

            else:

                print(
                    "No reliable command recognized."
                )

            return command

        except Exception as error:

            print(
                f"\nVoice error: {error}"
            )

            return (
                f"ERROR: {error}"
            )

        finally:

            if (
                temp_path is not None
                and temp_path.exists()
            ):

                try:

                    temp_path.unlink()

                except Exception:

                    pass