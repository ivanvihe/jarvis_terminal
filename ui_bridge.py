from jarvis_ui import JarvisApp
import threading
import time
from textual.message import Message

class UIBridge:
    def __init__(self):
        self.app = JarvisApp()
        self.input_queue = []
        self.jarvis_agent = None  # Referencia al agente
        self.app.on_user_input_callback = self._handle_input
        self.ready = False

        # No lanzamos app.run() aquí, dejamos que quien use UIBridge lo haga
        threading.Thread(target=self._wait_ready, daemon=True).start()

    def _wait_ready(self):
        while not self.app.is_ready:
            time.sleep(0.1)
        self.ready = True

    def _handle_input(self, text):
        """Este método se llama cuando el usuario envía texto desde la UI"""
        if hasattr(self, 'jarvis_agent') and self.jarvis_agent:
            threading.Thread(target=self._process_user_command, args=(text,), daemon=True).start()
        else:
            self.input_queue.append(text)

    def _process_user_command(self, text):
        """Procesa el comando del usuario"""
        try:
            if text.lower() in ["salir", "adios", "adiós"]:
                self.send_message("👋 Hasta luego.", sender="System")
                import os
                os._exit(0)
            else:
                if hasattr(self.jarvis_agent, 'process_text_command'):
                    self.jarvis_agent.process_text_command(text)
                else:
                    self.jarvis_agent.process_command(text)
        except Exception as e:
            self.send_message(f"❌ Error procesando comando: {e}", sender="Error")

    def set_jarvis_agent(self, agent):
        """Establece la referencia al agente"""
        self.jarvis_agent = agent

    def get_user_input(self):
        if self.input_queue:
            return self.input_queue.pop(0)
        return None

    def send_message(self, msg, sender="Jarvis"):
        if self.ready and msg.strip():
            try:
                self.app.post_message(self.app.MessageEvent(msg, sender))
                if hasattr(self.app, 'append_message'):
                    self.app.call_from_thread(self.app.append_message, msg, sender)
            except Exception as e:
                print(f"ERROR enviando mensaje a UI: {e}")
                print(f"Mensaje perdido: [{sender}] {msg}")
        elif not self.ready:
            print(f"UI not ready, message lost: [{sender}] {msg}")
        else:
            print(f"Empty message ignored: [{sender}] '{msg}'")

    def set_mic_status(self, active: bool):
        if self.ready:
            self.app.post_message(self.app.MicStatusEvent(active))

    def set_tts_engine(self, name: str):
        if self.ready:
            self.app.post_message(self.app.TTSEngineEvent(name))

    def set_ai_engine(self, name: str):
        if self.ready:
            self.app.post_message(self.app.AIEngineEvent(name))

    def update_memory_info(self, memory_entries, corrections):
        if self.ready:
            self.app.post_message(self.app.MemoryInfoEvent(memory_entries, corrections))

    def show_integrations(self, capabilities_dict):
        """Muestra integraciones activas en el sidebar"""
        if self.ready:
            try:
                names = list(capabilities_dict.keys())
                integrations_str = "\n".join(f"• {name}" for name in names) if names else "Ninguna"
                self.app.post_message(self.app.IntegrationsEvent(integrations_str))
            except Exception as e:
                print(f"⚠️ Error enviando IntegrationsEvent: {e}")
