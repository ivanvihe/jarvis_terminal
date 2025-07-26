from tts import init_tts, speak_response
from ai import ask_ai
from config_loader import WAKE_WORDS, DEBUG_STT, VOICE_INPUT_ENABLED
from stt import record_audio, speech_to_text
from memory import Memory
import threading
import time
import os
import sys

from ui_bridge import UIBridge  # 🚨 TUI bridge

class StdoutRedirector:
    def __init__(self, ui):
        self.ui = ui

    def write(self, text):
        if text.strip():
            self.ui.send_message(text.strip(), sender="Debug")

    def flush(self):
        pass  # para compatibilidad con sys.stdout

class JarvisAgent:
    def __init__(self, ui: UIBridge):
        self.ui = ui
        self.memory = Memory()
        self.tts_engine = init_tts()
        self.running = True
        self.listening = True
        self.waiting_for_command = False
        self.voice_input_enabled = VOICE_INPUT_ENABLED

        # Estado inicial en UI
        self.ui.send_message("Jarvis iniciado correctamente.", sender="System")
        self.ui.set_tts_engine(str(self.tts_engine.name))
        self.ui.update_memory_info(memory_entries=self.memory.size(), corrections=self.memory.corrections_count())

    def run(self):
        self.ui.send_message("Jarvis listo. Di 'Oye Jarvis' o escribe un comando.", sender="System")

        threading.Thread(target=self.text_input_loop, daemon=True).start()

        if self.voice_input_enabled:
            threading.Thread(target=self.audio_input_loop, daemon=True).start()
        else:
            self.ui.send_message("Modo solo texto activado (voice input desactivado).", sender="System")

        # Aquí NO hacemos wait_until_exit, porque la UI está en el hilo principal
        # La app principal queda bloqueada en ui.run()

    def audio_input_loop(self):
        while self.running:
            if not self.listening:
                time.sleep(0.1)
                continue

            if DEBUG_STT:
                self.ui.send_message("[DEBUG STT] Escuchando...", sender="Debug")

            self.ui.set_mic_status(True)
            filename = record_audio(duration=12)
            self.ui.set_mic_status(False)

            if not filename:
                continue

            text = speech_to_text(filename)
            if not text:
                continue

            text = text.lower()
            if DEBUG_STT:
                self.ui.send_message(f"[DEBUG STT] Texto recibido tras STT: '{text}'", sender="Debug")

            wake_detected = None
            for wake in WAKE_WORDS:
                if wake in text:
                    wake_detected = wake
                    break

            if wake_detected:
                after_wake = text.split(wake_detected, 1)[-1].strip(" ,")
                if after_wake:
                    self.process_command(after_wake)
                else:
                    self.ui.send_message("Te escucho. ¿Qué necesitas?", sender="Jarvis")
                    speak_response("Te escucho. ¿Qué necesitas?", self.tts_engine)
                    self.waiting_for_command = True
                    self.await_command_window()
            elif self.waiting_for_command:
                self.process_command(text)
                self.waiting_for_command = False

    def await_command_window(self, duration=10):
        start = time.time()
        while time.time() - start < duration and self.running:
            self.ui.set_mic_status(True)
            filename = record_audio(duration=12)
            self.ui.set_mic_status(False)

            if not filename:
                continue
            text = speech_to_text(filename)
            if not text:
                continue
            self.process_command(text)
            break

    def process_command(self, command):
        self.listening = False
        try:
            if not command or len(command.strip()) < 3:
                self.ui.send_message("⚠️ Comando muy corto, ignorado.", sender="System")
                self.ui.send_message("[DEBUG] Comando muy corto, ignorado.", sender="Debug")
                return

            noise_phrases = [
                "subtítulos por la comunidad de amara.org",
                "amara.org", "suscríbete", "gracias por ver"
            ]
            cmd_lower = command.lower()
            if any(phrase in cmd_lower for phrase in noise_phrases):
                self.ui.send_message(f"[DEBUG] Comando filtrado como ruido: {command}", sender="Debug")
                return

            self.ui.send_message(f"🧠 Pensando sobre: '{command}'", sender="Jarvis")
            self.ui.send_message(f"[DEBUG] Procesando comando: {command}", sender="Debug")

            response = ask_ai(command, self.memory)

            self.ui.send_message(f"[DEBUG] Respuesta AI: {response}", sender="Debug")
            print(f"DEBUG: Enviando mensaje a UI: {response[:60]} (sender=Jarvis)")
            self.ui.send_message(response, sender="Jarvis")
            speak_response(response, self.tts_engine)
            self.ui.update_memory_info(memory_entries=self.memory.size(), corrections=self.memory.corrections_count())

        except Exception as e:
            self.ui.send_message(f"❌ Error al procesar comando: {e}", sender="Error")
        finally:
            time.sleep(0.5)
            self.listening = True

    def text_input_loop(self):
        while self.running:
            try:
                user_input = self.ui.get_user_input()
                if user_input is None:
                    time.sleep(0.1)
                    continue

                user_input = user_input.strip()
                if user_input.lower() in ["salir", "adios", "adiós"]:
                    self.ui.send_message("👋 Hasta luego.", sender="System")
                    self.running = False
                    os._exit(0)
                elif user_input:
                    self.listening = False
                    self.process_command(user_input)
                    self.listening = True
            except Exception as e:
                self.ui.send_message(f"❌ Error en entrada de texto: {e}", sender="Error")
                break

if __name__ == "__main__":
    try:
        # Iniciamos UI en hilo principal
        ui = UIBridge()

        # Lanzamos backend en thread aparte
        def backend_loop():
            # Redirigimos stdout y stderr a la UI
            sys.stdout = StdoutRedirector(ui)
            sys.stderr = StdoutRedirector(ui)

            agent = JarvisAgent(ui)
            agent.run()

        import threading
        threading.Thread(target=backend_loop, daemon=True).start()

        # Ejecutamos la UI en main thread, bloquea aquí y no se cierra
        ui.app.run()

    except KeyboardInterrupt:
        print("\n👋 Jarvis desactivado por el usuario.")
