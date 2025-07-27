from tts import init_tts, speak_response
from ai import ask_ai
from config_loader import WAKE_WORDS, DEBUG_STT, VOICE_INPUT_ENABLED, TTS_MODE
from stt import record_audio, speech_to_text
from memory import Memory
import threading
import time
import os
import sys

from ui_bridge import UIBridge
from integrations_manager import create_integrations_manager
from config_display import format_config_display, get_config_summary

from events_core import EventManager
from config_reloader import ConfigFileWatcher

class ThreadSafeStdoutRedirector:
    def __init__(self, ui_bridge):
        self.ui_bridge = ui_bridge
        self.buffer = []
        self.lock = threading.Lock()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.processing = True
        self.processor_thread = threading.Thread(target=self._process_buffer, daemon=True)
        self.processor_thread.start()

    def write(self, text):
        if text.strip():
            with self.lock:
                self.buffer.append(text.strip())

    def flush(self):
        pass

    def _process_buffer(self):
        while self.processing:
            with self.lock:
                messages = self.buffer.copy()
                self.buffer.clear()
            for msg in messages:
                try:
                    sender = "Debug"
                    if "ERROR" in msg.upper() or "❌" in msg:
                        sender = "Error"
                    elif "WARNING" in msg.upper() or "⚠️" in msg:
                        sender = "System"
                    elif "[DEBUG" in msg:
                        sender = "Debug"
                    self.ui_bridge.send_message(msg, sender)
                except Exception as e:
                    self.original_stdout.write(f"Error redirecting: {e}\n")
            time.sleep(0.05)

    def stop(self):
        self.processing = False


class JarvisAgent:
    def __init__(self, ui: UIBridge):
        self.ui = ui
        self.memory = Memory()
        self.tts_engine = init_tts()
        self.running = True
        self.listening = True
        self.waiting_for_command = False
        self.voice_input_enabled = VOICE_INPUT_ENABLED
        self.integrations_manager = create_integrations_manager()
        self.ui.set_jarvis_agent(self)
        self._audio_thread = None

        self.ui.send_message("Jarvis iniciado correctamente.", sender="System")
        self.ui.set_tts_engine(str(self.tts_engine.name if hasattr(self.tts_engine, 'name') else "Local"))
        self.ui.update_memory_info(memory_entries=self.memory.size(), corrections=self.memory.corrections_count())

        capabilities = self.integrations_manager.get_all_capabilities()
        self.ui.show_integrations(capabilities)

        # Mostrar solo resumen al inicio
        summary = get_config_summary()
        self.ui.send_message(f"🚀 CONFIGURACIÓN DE INICIO: {summary}", sender="System")

        self.event_manager = EventManager()
        self.register_event_listeners()

    def show_full_configuration(self):
        """Muestra la configuración completa al usuario manualmente"""
        try:
            config_display = format_config_display()
            self.ui.send_message(config_display, sender="Config")
        except Exception as e:
            self.ui.send_message(f"⚠️ Error mostrando configuración: {e}", sender="Error")

    def register_event_listeners(self):
        config_watcher = ConfigFileWatcher(self.ui, self)
        self.event_manager.register_listener(config_watcher)

    def run(self):
        while not self.ui.ready:
            time.sleep(0.1)
        self.ui.send_message("Jarvis listo. Di 'Oye Jarvis' o escribe un comando.", sender="System")

        if self.voice_input_enabled:
            self.start_audio_input()
        else:
            self.ui.send_message("Modo solo texto activado (voice input desactivado).", sender="System")

    def start_audio_input(self):
        if self._audio_thread is None or not self._audio_thread.is_alive():
            self._audio_thread = threading.Thread(target=self.audio_input_loop, daemon=True)
            self._audio_thread.start()
            self.ui.send_message("🎤 Modo de voz activado.", sender="System")

    def stop_audio_input(self):
        if self._audio_thread and self._audio_thread.is_alive():
            self.ui.send_message("🔇 Modo de voz desactivado.", sender="System")

    def audio_input_loop(self):
        while self.running and self.voice_input_enabled:
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
                    self.process_command(after_wake, from_voice=True)
                else:
                    self.ui.send_message("Te escucho. ¿Qué necesitas?", sender="Jarvis")
                    speak_response("Te escucho. ¿Qué necesitas?", self.tts_engine)
                    self.waiting_for_command = True
                    self.await_command_window()
            elif self.waiting_for_command:
                self.process_command(text, from_voice=True)
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
            self.process_command(text, from_voice=True)
            break

    def process_command(self, command, from_voice=True):
        self.listening = False
        try:
            self.ui.send_message(f"🔴 Procesando comando: '{command}'", sender="Debug")
            if not command or len(command.strip()) < 3:
                self.ui.send_message("⚠️ Comando muy corto, ignorado.", sender="System")
                return

            # Comando especial: mostrar configuración completa (soporta varias frases)
            normalized = command.lower()
            config_phrases = [
                "ver configuración", "ver la configuración", "muestra configuración",
                "muestra toda la configuración", "quiero ver la configuración", "mostrar configuración"
            ]
            if any(phrase in normalized for phrase in config_phrases):
                self.ui.send_message("📋 Mostrando configuración completa...", sender="System")
                self.show_full_configuration()
                return

            self.ui.send_message(f"🧬 Pensando sobre: '{command}'", sender="Jarvis")

            integration_response = self.integrations_manager.process_command(command)
            if integration_response:
                response = integration_response.get("response", "Comando procesado por integración.")
            else:
                response = ask_ai(command, self.memory)

            if response and response.strip():
                self.ui.send_message(response, sender="Jarvis")
                if from_voice and self.voice_input_enabled:
                    self.ui.send_message("🔊 Reproduciendo por voz...", sender="System")
                    speak_response(response, self.tts_engine)
            else:
                self.ui.send_message("⚠️ No se pudo generar respuesta", sender="System")

            self.ui.update_memory_info(memory_entries=self.memory.size(), corrections=self.memory.corrections_count())

        except Exception as e:
            self.ui.send_message(f"❌ Error al procesar comando: {e}", sender="Error")
        finally:
            self.ui.send_message("🔴 Procesamiento completado", sender="Debug")
            time.sleep(0.5)
            self.listening = True

    def apply_config_changes(self):
        from config_loader import VOICE_INPUT_ENABLED, TTS_MODE, AI_PROVIDER
        old_voice_enabled = self.voice_input_enabled
        self.voice_input_enabled = VOICE_INPUT_ENABLED

        self.ui.send_message(f"📡 Aplicando cambios de configuración...", sender="System")
        self.ui.send_message(f"   • voice_input_enabled: {old_voice_enabled} → {self.voice_input_enabled}", sender="System")

        if old_voice_enabled != self.voice_input_enabled:
            if self.voice_input_enabled:
                self.start_audio_input()
            else:
                self.stop_audio_input()

        try:
            old_tts_name = str(self.tts_engine.name if hasattr(self.tts_engine, 'name') else "Local")
            new_tts_engine = init_tts()
            new_tts_name = str(new_tts_engine.name if hasattr(new_tts_engine, 'name') else "Local")
            if TTS_MODE == "elevenlabs":
                new_tts_name = "ElevenLabs"
            elif TTS_MODE == "local":
                new_tts_name = "Local"

            self.tts_engine = new_tts_engine
            self.ui.set_tts_engine(new_tts_name)

            if old_tts_name != new_tts_name:
                self.ui.send_message(f"🔊 Motor TTS actualizado: {old_tts_name} → {new_tts_name}", sender="System")
        except Exception as e:
            self.ui.send_message(f"⚠️ Error actualizando TTS: {e}", sender="System")

        try:
            ai_engine_name = AI_PROVIDER.upper() if AI_PROVIDER != "local" else "Local"
            self.ui.set_ai_engine(ai_engine_name)
            self.ui.send_message(f"🤖 Motor AI: {ai_engine_name}", sender="System")
        except Exception as e:
            self.ui.send_message(f"⚠️ Error actualizando AI engine info: {e}", sender="System")

        try:
            self.ui.send_message("🔄 Recargando integraciones...", sender="System")
            self.integrations_manager.shutdown_all()
            self.integrations_manager = create_integrations_manager()
            capabilities = self.integrations_manager.get_all_capabilities()
            self.ui.show_integrations(capabilities)
            integration_names = list(capabilities.keys())
            if integration_names:
                self.ui.send_message(f"🧩 Integraciones recargadas: {', '.join(integration_names)}", sender="System")
            else:
                self.ui.send_message("🧩 No hay integraciones activas", sender="System")
        except Exception as e:
            self.ui.send_message(f"⚠️ Error recargando integraciones: {e}", sender="System")

        self.ui.update_memory_info(
            memory_entries=self.memory.size(), 
            corrections=self.memory.corrections_count()
        )

        self.ui.send_message("✅ Cambios aplicados", sender="System")
        
        # Mostrar solo resumen actualizado
        summary = get_config_summary()
        self.ui.send_message(f"🔄 CONFIGURACIÓN ACTUAL: {summary}", sender="System")

    def listen_for_confirmation(self, timeout=4):
        if not self.voice_input_enabled:
            self.ui.send_message("⚠️ No se puede escuchar, voz desactivada.", sender="System")
            return None

        self.ui.send_message("🎤 Esperando confirmación...", sender="System")
        self.ui.set_mic_status(True)
        filename = record_audio(duration=timeout)
        self.ui.set_mic_status(False)
        if not filename:
            return None
        text = speech_to_text(filename)
        if text:
            self.ui.send_message(f"👂 Escuchado: '{text}'", sender="Jarvis")
        return text

def main():
    try:
        ui = UIBridge()
        redirector = ThreadSafeStdoutRedirector(ui)
        sys.stdout = redirector
        sys.stderr = redirector

        def backend_loop():
            try:
                agent = JarvisAgent(ui)
                agent.run()
            except Exception as e:
                ui.send_message(f"❌ Error en backend: {e}", sender="Error")

        threading.Thread(target=backend_loop, daemon=True).start()
        ui.app.run()

    except KeyboardInterrupt:
        print("\n👋 Jarvis desactivado por el usuario.")
    finally:
        if 'redirector' in locals():
            redirector.stop()

if __name__ == "__main__":
    main()
