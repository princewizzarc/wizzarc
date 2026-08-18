from PySide6.QtCore import QThread, Signal


class VoiceWorker(QThread):

    result_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, voice_engine):
        super().__init__()

        self.voice_engine = voice_engine


    def run(self):
        try:
            text = self.voice_engine.listen_once()

            self.result_ready.emit(text)

        except Exception as error:
            self.error_occurred.emit(
                str(error)
            )