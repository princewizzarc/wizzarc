from PySide6.QtCore import QThread, Signal

from core.crash_logger import log_exception
from voice.speech_engine import SpeechEngine


class SpeechWorker(QThread):

    error_occurred = Signal(str)

    def __init__(
        self,
        text,
        parent=None,
    ):
        super().__init__(parent)

        self.text = str(text).strip()

    def run(self):

        if not self.text:
            return

        try:

            engine = SpeechEngine()

            engine.speak(
                self.text
            )

        except Exception as error:

            log_exception(
                type(error),
                error,
                error.__traceback__,
                source="SpeechWorker",
            )

            self.error_occurred.emit(
                str(error)
            )