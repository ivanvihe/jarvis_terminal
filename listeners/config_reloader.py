# listeners/config_reloader.py

import os
import time
from events_core import EventListener
from config_loader import reload_config
import threading

class ConfigFileWatcher(EventListener):
    def __init__(self, ui_bridge, jarvis_agent, filepath="config.json", check_interval=1.0):
        super().__init__(name="ConfigFileWatcher")
        self.ui = ui_bridge
        self.jarvis_agent = jarvis_agent
        self.filepath = filepath
        self.check_interval = check_interval
        self.last_mtime = self.get_mtime()

    def get_mtime(self):
        try:
            return os.path.getmtime(self.filepath)
        except FileNotFoundError:
            return None

    def run(self):
        self.ui.send_message(f"👁️ ConfigFileWatcher iniciado para {self.filepath}", sender="Debug")
        while self.running:
            current_mtime = self.get_mtime()
            if current_mtime and current_mtime != self.last_mtime:
                self.last_mtime = current_mtime
                self.ui.send_message("⚠️ Detectado cambio en config.json", sender="System")

                # Lanzar hilo para no bloquear el watcher
                threading.Thread(target=self.prompt_reload, daemon=True).start()

            time.sleep(self.check_interval)

    def prompt_reload(self):
        self.ui.send_message("¿Deseas aplicar la nueva configuración? Responde 'sí' o 'no'.", sender="Jarvis")
        confirmation = self.jarvis_agent.listen_for_confirmation(timeout=4)

        if confirmation and "sí" in confirmation.lower():
            reload_config()  # Recarga config en config_loader
            self.ui.send_message("🔄 Recargando configuración...", sender="System")
            self.jarvis_agent.apply_config_changes()
        else:
            self.ui.send_message("❎ Configuración NO recargada.", sender="System")
