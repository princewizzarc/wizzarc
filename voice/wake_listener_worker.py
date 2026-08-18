from __future__ import annotations

import re
import threading

from PySide6.QtCore import QThread, Signal

from core.crash_logger import log_exception


class WakeListenerWorker(QThread):
    """
    Improvement #6 - Step 1

    Continuously listens for a wake phrase such as:
        "wizzarc"
        "hey wizzarc"

    This worker does NOT execute commands.
    It only emits wake_detected when the wake phrase is heard.

    The existing VoiceWorker remains untouched and will later be used
    for the actual command after wake-up.
    """

    wake_detected = Signal(str)
    heard_text = Signal(str)
    status_changed = Signal(str)
    error_occurred = Signal(str)

    DEFAULT_WAKE_PHRASES = (
        "wizzarc",
        "hey wizzarc",
        "ok wizzarc",
        "okay wizzarc",
    )

    def __init__(
        self,
        voice_engine,
        wake_phrases=None,
        parent=None,
    ):
        super().__init__(parent)

        self.voice_engine = voice_engine

        phrases = (
            wake_phrases
            if wake_phrases is not None
            else self.DEFAULT_WAKE_PHRASES
        )

        self.wake_phrases = tuple(
            self._normalize_text(item)
            for item in phrases
            if str(item).strip()
        )

        self._stop_event = threading.Event()

    # =====================================================
    # CONTROL
    # =====================================================

    def stop(self):
        """
        Ask the listener loop to stop.

        record_audio() may still need to finish its current short
        listening cycle before the thread exits.
        """

        self._stop_event.set()

        if self.isRunning():
            self.status_changed.emit(
                "stopping"
            )

    def should_stop(self):
        return self._stop_event.is_set()

    # =====================================================
    # TEXT HELPERS
    # =====================================================

    @staticmethod
    def _normalize_text(text):
        text = str(text).lower().strip()

        text = re.sub(
            r"[^\w\s]+",
            " ",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def _contains_wake_phrase(
        self,
        text,
    ):
        normalized = self._normalize_text(
            text
        )

        if not normalized:
            return False

        for phrase in self.wake_phrases:

            # Word-boundary style matching avoids accidental matches
            # inside unrelated longer words.
            pattern = (
                r"(?<!\w)"
                + re.escape(phrase)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            ):
                return True

        return False

    # =====================================================
    # RAW WAKE TRANSCRIPTION
    # =====================================================

    def _transcribe_wake_audio(
        self,
        temp_path,
    ):
        """
        Uses the Whisper model already loaded by VoiceEngine, but
        returns RAW recognized speech instead of passing it through
        VoiceEngine.match_command().
        """

        segments, _ = (
            self.voice_engine
            .model
            .transcribe(
                str(temp_path),
                beam_size=1,
                vad_filter=True,
                condition_on_previous_text=False,
                initial_prompt=(
                    "Wake phrase for a desktop AI assistant. "
                    "The assistant is named WizzArc. "
                    "Possible phrases: WizzArc, Hey WizzArc, "
                    "Okay WizzArc."
                ),
            )
        )

        parts = []

        for segment in segments:
            text = str(
                segment.text
            ).strip()

            if text:
                parts.append(
                    text
                )

        return " ".join(
            parts
        ).strip()

    # =====================================================
    # ONE WAKE LISTEN CYCLE
    # =====================================================

    def listen_for_wake_once(
        self,
    ):
        temp_path = None

        try:
            audio = (
                self.voice_engine
                .record_audio()
            )

            if (
                self.should_stop()
                or
                audio is None
            ):
                return False

            temp_path = (
                self.voice_engine
                .save_temp_audio(
                    audio
                )
            )

            raw_text = (
                self._transcribe_wake_audio(
                    temp_path
                )
            )

            if raw_text:
                self.heard_text.emit(
                    raw_text
                )

            if self._contains_wake_phrase(
                raw_text
            ):
                self.wake_detected.emit(
                    raw_text
                )
                return True

            return False

        finally:
            if (
                temp_path is not None
                and temp_path.exists()
            ):
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    # =====================================================
    # CONTINUOUS LOOP
    # =====================================================

    def run(self):
        self._stop_event.clear()

        self.status_changed.emit(
            "wake-listening"
        )

        try:
            while not self.should_stop():

                try:
                    detected = (
                        self.listen_for_wake_once()
                    )

                    if detected:

                        # Stop listening immediately after wake-up.
                        # Main UI will later start the normal VoiceWorker
                        # for the user's actual command, then create/start
                        # this wake listener again.
                        self.status_changed.emit(
                            "wake-detected"
                        )
                        break

                except Exception as error:

                    if self.should_stop():
                        break

                    log_exception(
                        type(error),
                        error,
                        error.__traceback__,
                        source="WakeListenerWorker Loop",
                    )

                    self.error_occurred.emit(
                        str(error)
                    )

            if self.should_stop():
                self.status_changed.emit(
                    "stopped"
                )

        except Exception as error:

            log_exception(
                type(error),
                error,
                error.__traceback__,
                source="WakeListenerWorker",
            )

            self.error_occurred.emit(
                str(error)
            )