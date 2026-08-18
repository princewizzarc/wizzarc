import threading

import pyttsx3


class SpeechEngine:

    def __init__(self):

        self.lock = threading.Lock()

    def speak(self, text):

        if not text:
            return

        # Run speech separately so UI doesn't freeze
        thread = threading.Thread(
            target=self._speak,
            args=(text,),
            daemon=True
        )

        thread.start()

    def _speak(self, text):

        with self.lock:

            try:

                engine = pyttsx3.init()

                engine.setProperty(
                    "rate",
                    180
                )

                engine.setProperty(
                    "volume",
                    1.0
                )

                engine.say(text)

                engine.runAndWait()

                engine.stop()

            except Exception as error:

                print(
                    f"TTS error: {error}"
                )