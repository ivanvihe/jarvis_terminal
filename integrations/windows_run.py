# integrations/windows_run.py - Integración para ejecutar apps de Windows

import subprocess
import os
from typing import List, Optional, Dict, Any
from integrations_manager import BaseIntegration

class WindowsRunIntegration(BaseIntegration):
    """Integración para lanzar aplicaciones de Windows desde comandos de voz o texto"""

    def initialize(self) -> bool:
        """Inicializa la integración verificando que estamos en Windows"""
        if os.name != 'nt':
            print("❌ WindowsRun solo es compatible con Windows.")
            self.enabled = False
            return False

        self.apps_config = self.config.get("apps", {})
        if not self.apps_config:
            print("⚠️ No hay aplicaciones definidas en config.json > integrations > windows_run > apps")
        else:
            print(f"✅ WindowsRun cargado con {len(self.apps_config)} apps configuradas")
        return True

    def get_capabilities(self) -> List[str]:
        """Palabras clave que detectan que esta integración puede usarse"""
        return [
            "abrir", "abre", "ejecuta", "inicia", "lanzar", "start", "open", "run"
        ]

    def handle_command(self, command: str, context: dict = None) -> Optional[Dict[str, Any]]:
        """Procesa el comando y lanza la aplicación correspondiente"""
        command_lower = command.lower()
        matched_app = None

        # Buscar si alguna app de la config está mencionada en el comando
        for app_name in self.apps_config:
            if app_name.lower() in command_lower:
                matched_app = app_name
                break

        if not matched_app:
            return {"response": "No encontré qué aplicación abrir. Revisa la configuración."}

        app_path = self.apps_config[matched_app]
        try:
            subprocess.Popen(app_path, shell=True)
            return {"response": f"✅ Lanzando {matched_app}..."}
        except Exception as e:
            return {"response": f"❌ Error al intentar abrir {matched_app}: {e}"}

    def shutdown(self):
        """No se requiere limpieza para esta integración"""
        pass
