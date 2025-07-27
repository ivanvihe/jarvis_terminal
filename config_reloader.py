# config_reloader.py

import os
import time
import threading
from events_core import EventListener
from config_loader import reload_config
from tts import speak_response

class ConfigFileWatcher(EventListener):
    def __init__(self, ui, agent, filepath="config.json", check_interval=1.0):
        super().__init__(name="ConfigWatcher")
        self.ui = ui
        self.agent = agent
        self.filepath = filepath
        self.check_interval = check_interval
        self.last_modified = os.path.getmtime(self.filepath) if os.path.exists(self.filepath) else 0
        self.waiting_for_response = False

    def run(self):
        while self.running:
            try:
                if not os.path.exists(self.filepath):
                    time.sleep(self.check_interval)
                    continue
                    
                current_mtime = os.path.getmtime(self.filepath)
                if current_mtime != self.last_modified:
                    self.last_modified = current_mtime
                    self.handle_config_change()
                    
            except Exception as e:
                self.ui.send_message(f"❌ Error en config watcher: {e}", sender="Error")
            time.sleep(self.check_interval)

    def handle_config_change(self):
        """Maneja el cambio detectado en config.json"""
        self.ui.send_message("🟡 Detectado cambio en config.json", sender="System")
        
        # Pausar el agente para evitar interferencias
        old_listening = self.agent.listening
        self.agent.listening = False
        self.waiting_for_response = True
        
        try:
            # Preguntar si quiere recargar
            message = "Se ha detectado un cambio en configuración. ¿Deseas recargarlo? (sí/no)"
            self.ui.send_message(message, sender="System")
            
            # Reproducir por voz si está habilitado
            if self.agent.voice_input_enabled:
                speak_response(message, self.agent.tts_engine)
            
            # Esperar respuesta (texto o voz)
            response = self.wait_for_user_response(timeout=10)
            
            if response:
                response_lower = response.lower().strip()
                if any(word in response_lower for word in ["sí", "si", "yes", "s", "ok", "vale"]):
                    self.reload_configuration()
                elif any(word in response_lower for word in ["no", "n", "nope", "cancel", "cancelar"]):
                    self.cancel_reload()
                else:
                    self.ui.send_message("❓ Respuesta no reconocida. Cancelando recarga.", sender="System")
                    self.cancel_reload()
            else:
                self.ui.send_message("⏰ Tiempo agotado. Cancelando recarga.", sender="System")
                self.cancel_reload()
                
        finally:
            # Restaurar estado del agente
            self.waiting_for_response = False
            self.agent.listening = old_listening

    def wait_for_user_response(self, timeout=10):
        """Espera respuesta del usuario por texto o voz"""
        start_time = time.time()
        
        # Configurar callback temporal para capturar input
        original_callback = self.agent.ui.app.on_user_input_callback
        response_received = threading.Event()
        user_response = [None]  # Lista para poder modificar desde callback
        
        def temp_callback(text):
            user_response[0] = text
            response_received.set()
        
        self.agent.ui.app.on_user_input_callback = temp_callback
        
        try:
            # Si el modo voz está habilitado, también escuchar por voz
            if self.agent.voice_input_enabled:
                def voice_listener():
                    from stt import record_audio, speech_to_text
                    self.ui.set_mic_status(True)
                    filename = record_audio(duration=timeout)
                    self.ui.set_mic_status(False)
                    if filename:
                        text = speech_to_text(filename)
                        if text:
                            user_response[0] = text
                            response_received.set()
                
                voice_thread = threading.Thread(target=voice_listener, daemon=True)
                voice_thread.start()
            
            # Esperar respuesta con timeout
            if response_received.wait(timeout=timeout):
                return user_response[0]
            else:
                return None
                
        finally:
            # Restaurar callback original
            self.agent.ui.app.on_user_input_callback = original_callback

    def reload_configuration(self):
        """Ejecuta la recarga de configuración"""
        self.ui.send_message("🔄 Recargando configuración...", sender="System")
        
        if reload_config():
            # Aplicar cambios al agente
            self.agent.apply_config_changes()
            self.ui.send_message("✅ Configuración recargada correctamente.", sender="System")
            
            if self.agent.voice_input_enabled:
                speak_response("Configuración recargada correctamente.", self.agent.tts_engine)
        else:
            self.ui.send_message("❌ Error al recargar configuración.", sender="Error")
            if self.agent.voice_input_enabled:
                speak_response("Error al recargar configuración.", self.agent.tts_engine)

    def cancel_reload(self):
        """Cancela la recarga de configuración"""
        self.ui.send_message("❌ Recarga de configuración cancelada.", sender="System")
        
        # Si estaba en modo voz y ahora voice_input está deshabilitado, informar
        if self.agent.voice_input_enabled:
            speak_response("Recarga cancelada.", self.agent.tts_engine)