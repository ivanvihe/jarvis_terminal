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
                    self.jarvis_agent.process_command(text, from_voice=False)
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
        """Envía mensaje a la interfaz de manera thread-safe"""
        if self.ready and msg.strip():
            try:
                # Usar el sistema de eventos para thread-safety
                self.app.post_message(self.app.MessageEvent(msg, sender))
            except Exception as e:
                print(f"ERROR enviando mensaje a UI: {e}")
                print(f"Mensaje perdido: [{sender}] {msg}")
        elif not self.ready:
            print(f"UI not ready, message lost: [{sender}] {msg}")

    def set_mic_status(self, active: bool):
        """Establece el estado del micrófono"""
        if self.ready:
            try:
                self.app.post_message(self.app.MicStatusEvent(active))
            except Exception as e:
                print(f"Error setting mic status: {e}")

    def set_tts_engine(self, name: str):
        """Establece el nombre del motor TTS"""
        if self.ready:
            try:
                self.app.post_message(self.app.TTSEngineEvent(name))
            except Exception as e:
                print(f"Error setting TTS engine: {e}")

    def set_ai_engine(self, name: str):
        """Establece el nombre del motor AI"""
        if self.ready:
            try:
                self.app.post_message(self.app.AIEngineEvent(name))
            except Exception as e:
                print(f"Error setting AI engine: {e}")

    def update_memory_info(self, memory_entries, corrections):
        """Actualiza la información de memoria y correcciones"""
        if self.ready:
            try:
                self.app.post_message(self.app.MemoryInfoEvent(memory_entries, corrections))
            except Exception as e:
                print(f"Error updating memory info: {e}")

    def show_integrations(self, capabilities_dict):
        """Muestra integraciones activas en el sidebar"""
        if self.ready:
            try:
                if isinstance(capabilities_dict, dict):
                    integrations_lines = []
                    for name, capabilities in capabilities_dict.items():
                        # Usar formato similar al config_display
                        status = "✅" if capabilities else "❌"
                        caps_str = ", ".join(capabilities[:2]) if capabilities else "Sin capacidades"
                        if len(capabilities) > 2:
                            caps_str += f" (+{len(capabilities)-2} más)"
                        integrations_lines.append(f"{status} [bold]{name}[/bold]")
                        integrations_lines.append(f"   {caps_str}")
                    
                    integrations_str = "\n".join(integrations_lines) if integrations_lines else "[dim]Ninguna activa[/dim]"
                else:
                    # Si se pasa directamente un string (para compatibilidad)
                    integrations_str = str(capabilities_dict) if capabilities_dict else "[dim]Ninguna activa[/dim]"
                
                self.app.post_message(self.app.IntegrationsEvent(integrations_str))
            except Exception as e:
                print(f"⚠️ Error enviando IntegrationsEvent: {e}")
                # Fallback
                self.app.post_message(self.app.IntegrationsEvent("[red]Error cargando integraciones[/red]"))