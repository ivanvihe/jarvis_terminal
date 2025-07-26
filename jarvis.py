from tts import init_tts, speak_response
from ai import ask_ai
from config_loader import WAKE_WORDS, DEBUG_STT, VOICE_INPUT_ENABLED
from stt import record_audio, speech_to_text
from memory import Memory
import threading
import time
import os
import sys

from ui_bridge import UIBridge

class ThreadSafeStdoutRedirector:
    def __init__(self, ui_bridge):
        self.ui_bridge = ui_bridge
        self.buffer = []
        self.lock = threading.Lock()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Hilo para procesar el buffer
        self.processing = True
        self.processor_thread = threading.Thread(target=self._process_buffer, daemon=True)
        self.processor_thread.start()

    def write(self, text):        
        if text.strip():  # Solo procesar si no está vacío
            with self.lock:
                self.buffer.append(text.strip())

    def flush(self):
        pass

    def _process_buffer(self):
        while self.processing:
            with self.lock:
                if self.buffer:
                    messages = self.buffer.copy()
                    self.buffer.clear()
                else:
                    messages = []
            
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
            
            time.sleep(0.05)  # Procesamiento más frecuente

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

        # ✅ IMPORTANTE: Establecer la referencia en UIBridge
        self.ui.set_jarvis_agent(self)

        # Estado inicial en UI
        self.ui.send_message("Jarvis iniciado correctamente.", sender="System")
        self.ui.set_tts_engine(str(self.tts_engine.name if hasattr(self.tts_engine, 'name') else "Local"))
        self.ui.update_memory_info(memory_entries=self.memory.size(), corrections=self.memory.corrections_count())

    def run(self):
        # Esperar a que UI esté lista
        while not self.ui.ready:
            time.sleep(0.1)
            
        self.ui.send_message("Jarvis listo. Di 'Oye Jarvis' o escribe un comando.", sender="System")

        # ✅ Solo iniciar audio loop, el text input se maneja directamente en UIBridge
        if self.voice_input_enabled:
            threading.Thread(target=self.audio_input_loop, daemon=True).start()
        else:
            self.ui.send_message("Modo solo texto activado (voice input desactivado).", sender="System")

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
                    self.process_command(after_wake, from_voice=True)  # Desde voz
                else:
                    self.ui.send_message("Te escucho. ¿Qué necesitas?", sender="Jarvis")
                    speak_response("Te escucho. ¿Qué necesitas?", self.tts_engine)
                    self.waiting_for_command = True
                    self.await_command_window()
            elif self.waiting_for_command:
                self.process_command(text, from_voice=True)  # Desde voz
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
            self.process_command(text, from_voice=True)  # Desde voz
            break

    def process_command(self, command, from_voice=True):
        """Procesa comandos (principalmente de voz)"""
        self.listening = False  # Parar escucha durante procesamiento
        try:
            # Debug inicial
            self.ui.send_message(f"🔴 Procesando comando: '{command}' (from_voice={from_voice})", sender="Debug")
            
            if not command or len(command.strip()) < 3:
                self.ui.send_message("⚠️ Comando muy corto, ignorado.", sender="System")
                return

            noise_phrases = [
                "subtítulos por la comunidad de amara.org",
                "amara.org", "suscríbete", "gracias por ver"
            ]
            cmd_lower = command.lower()
            if any(phrase in cmd_lower for phrase in noise_phrases):
                self.ui.send_message(f"[DEBUG] Comando filtrado como ruido: {command}", sender="Debug")
                return

            # Mostrar que estamos procesando
            self.ui.send_message(f"🧠 Pensando sobre: '{command}'", sender="Jarvis")
            
            # Procesar con IA real
            try:
                from ai import ask_ai
                self.ui.send_message(f"[DEBUG] Llamando a ask_ai...", sender="Debug")
                response = ask_ai(command, self.memory)
                self.ui.send_message(f"[DEBUG] Respuesta recibida: '{response[:100]}...'", sender="Debug")
            except ImportError as e:
                self.ui.send_message(f"❌ Error importando ask_ai: {e}", sender="Error")
                response = f"Error: No se pudo cargar el módulo de IA. {e}"
            except Exception as e:
                self.ui.send_message(f"❌ Error en ask_ai: {e}", sender="Error")
                response = f"Error procesando con IA: {e}"

            # Mostrar la respuesta EN TEXTO SIEMPRE
            if response and response.strip():
                self.ui.send_message(response, sender="Jarvis")
                
                # Solo hablar si viene de voz
                if from_voice:
                    self.ui.send_message("🔊 Reproduciendo por voz...", sender="System")
                    try:
                        speak_response(response, self.tts_engine)
                    except Exception as e:
                        self.ui.send_message(f"❌ Error en TTS: {e}", sender="Error")
                else:
                    self.ui.send_message("📝 Solo texto (sin voz)", sender="System")
            else:
                self.ui.send_message("⚠️ No se pudo generar respuesta", sender="System")
                
            # Actualizar memoria - con manejo de errores
            try:
                if hasattr(self.memory, 'size') and hasattr(self.memory, 'corrections_count'):
                    self.ui.update_memory_info(
                        memory_entries=self.memory.size(), 
                        corrections=self.memory.corrections_count()
                    )
                else:
                    self.ui.send_message("[DEBUG] Memory object sin métodos size/corrections_count", sender="Debug")
            except Exception as e:
                self.ui.send_message(f"[DEBUG] Error actualizando memoria: {e}", sender="Debug")

        except Exception as e:
            self.ui.send_message(f"❌ Error al procesar comando: {e}", sender="Error")
            import traceback
            self.ui.send_message(f"❌ Traceback: {traceback.format_exc()}", sender="Error")
        finally:
            # IMPORTANTE: Reactivar la escucha
            self.ui.send_message("🔴 Procesamiento completado", sender="Debug")
            time.sleep(0.5)
            self.listening = True

    def process_text_command(self, command):
        """Procesa comandos de texto (sin voz)"""
        self.process_command(command, from_voice=False)

    def text_input_loop(self):
        """Método mantenido para compatibilidad, pero ya no se usa activamente"""
        pass  # El procesamiento de texto ahora se hace directamente desde UIBridge

def main():
    try:
        # Iniciamos UI bridge
        ui = UIBridge()
        
        # Configurar redirección de stdout/stderr ANTES de iniciar el backend
        redirector = ThreadSafeStdoutRedirector(ui)
        sys.stdout = redirector
        sys.stderr = redirector
        
        # Lanzamos backend en thread aparte
        def backend_loop():
            try:
                agent = JarvisAgent(ui)
                agent.run()
            except Exception as e:
                ui.send_message(f"❌ Error en backend: {e}", sender="Error")

        threading.Thread(target=backend_loop, daemon=True).start()

        # Ejecutamos la UI en main thread
        ui.app.run()

    except KeyboardInterrupt:
        print("\n👋 Jarvis desactivado por el usuario.")
    finally:
        # Restaurar stdout original al salir
        if 'redirector' in locals():
            redirector.stop()
            redirector.restore_original()

if __name__ == "__main__":
    main()