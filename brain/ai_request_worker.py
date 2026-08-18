from PySide6.QtCore import QThread, Signal

from core.crash_logger import log_exception


class AIRequestWorker(QThread):

    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(
        self,
        ai_controller,
        user_text,
        parent=None,
    ):
        super().__init__(parent)

        self.ai_controller = ai_controller
        self.user_text = str(
            user_text
        ).strip()

    def run(self):

        try:

            result = (
                self.ai_controller
                .handle(
                    self.user_text
                )
            )

            self.result_ready.emit(
                result
            )

        except Exception as error:

            log_exception(
                type(error),
                error,
                error.__traceback__,
                source="AIRequestWorker",
            )

            self.error_occurred.emit(
                str(error)
            )