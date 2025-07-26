import threading
import time
from stt import record_audio, speech_to_text
from config_loader import WAKE_WORD, INTERACTIVE_MODE_DURATION, VOICE_INPUT_ENABLED

DEBUG_INPUT = True

class InputHandler:
    def __init__(self):
        self.listening = True
        self.interactive_until = 0

    def get_text_input(self):
        try:
            command = input("📅 Command ('salir' to quit): ").strip()
            return command
        except EOFError:
            return "salir"

    def get_voice_input(self):
        filename = record_audio()
        if filename:
            text = speech_to_text(filename)
            return text
        return ""

    def process_input(self, text):
        text_lower = text.lower()
        wake = WAKE_WORD.lower()

        if wake in text_lower:
            after_wake = text_lower.split(wake, 1)[-1].strip()
            if after_wake:
                if DEBUG_INPUT:
                    print(f"[DEBUG] Wake word '{wake}' + command detected: {after_wake}")
                return after_wake, True
            else:
                if DEBUG_INPUT:
                    print(f"[DEBUG] Wake word '{wake}' detected alone. Activating interactive mode.")
                self.interactive_until = time.time() + INTERACTIVE_MODE_DURATION
                return "", True
        elif self.interactive_until > time.time():
            if DEBUG_INPUT:
                print(f"[DEBUG] In interactive mode: command received '{text}'")
            return text_lower.strip(), True
        else:
            if DEBUG_INPUT:
                print(f"[DEBUG] Command outside wake word context: '{text}'")
            return "", False

    def get_input(self):
        while self.listening:
            try:
                # Prioritize text input if available
                if self.is_input_available():
                    text = self.get_text_input()
                    if text:
                        cmd, valid = self.process_input(text)
                        if valid:
                            return cmd
                else:
                    # Only try voice input if enabled in config
                    if VOICE_INPUT_ENABLED:
                        text = self.get_voice_input()
                        if text:
                            cmd, valid = self.process_input(text)
                            if valid:
                                return cmd
                    else:
                        # If voice input disabled, just wait a bit to avoid busy loop
                        time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n👋 Jarvis deactivated.")
                return "salir"

    def is_input_available(self):
        import sys
        import select
        return select.select([sys.stdin], [], [], 0.1)[0]
