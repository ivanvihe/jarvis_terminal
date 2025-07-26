from jarvis_ui import JarvisApp
import threading
import time

class UIBridge:
    def __init__(self):
        self.app = JarvisApp()
        self.input_queue = []
        self.app.on_user_input_callback = self._handle_input
        self.ready = False

        # No lanzamos app.run() aquí, dejamos que quien use UIBridge lo haga
        # Solo esperamos a que UI esté lista
        threading.Thread(target=self._wait_ready, daemon=True).start()

    def _wait_ready(self):
        while not self.app.is_ready:
            time.sleep(0.1)
        self.ready = True

    def _handle_input(self, text):
        self.input_queue.append(text)

    def get_user_input(self):
        if self.input_queue:
            return self.input_queue.pop(0)
        return None

    def send_message(self, msg, sender="Jarvis"):
        if self.ready:
            print(f"UIBridge: enviando mensaje '{msg[:30]}...' sender={sender}")
            self.app.append_message(msg, sender)

    def set_mic_status(self, active: bool):
        if self.ready:
            self.app.set_mic_status(active)

    def set_tts_engine(self, name: str):
        if self.ready:
            self.app.set_tts_engine(name)

    def set_ai_engine(self, name: str):
        if self.ready:
            self.app.set_ai_engine(name)

    def update_memory_info(self, memory_entries, corrections):
        if self.ready:
            self.app.update_memory_info(memory_entries, corrections)
