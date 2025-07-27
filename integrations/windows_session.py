import os
import ctypes
from typing import List, Optional, Dict, Any
from integrations_manager import BaseIntegration

class WindowsSessionIntegration(BaseIntegration):
    """Integración para controlar sesión y estado del sistema Windows"""

    def initialize(self) -> bool:
        if os.name != 'nt':
            print("❌ WindowsSession solo funciona en Windows.")
            self.enabled = False
            return False
        print("✅ WindowsSession listo")
        return True

    def get_capabilities(self) -> List[str]:
        return ["reiniciar", "apagar", "bloquear", "cerrar sesión", "hibernar", "suspender"]

    def handle_command(self, command: str, context: dict = None) -> Optional[Dict[str, Any]]:
        cmd = command.lower()
        
        try:
            if "reiniciar" in cmd:
                os.system("shutdown /r /t 0")
                return {"response": "🔄 Reiniciando Windows..."}
            
            if "apagar" in cmd:
                os.system("shutdown /s /t 0")
                return {"response": "⏻ Apagando Windows..."}
            
            if "bloquear" in cmd:
                ctypes.windll.user32.LockWorkStation()
                return {"response": "🔒 Sesión bloqueada."}
            
            if "cerrar sesión" in cmd or "logout" in cmd:
                os.system("shutdown /l")
                return {"response": "🚪 Cerrando sesión..."}
            
            if "hibernar" in cmd:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return {"response": "💤 Hibernando sistema..."}
            
            if "suspender" in cmd or "sleep" in cmd:
                # Suspender es más complicado; hibernar es lo más común vía comando
                os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")
                return {"response": "😴 Suspender sistema..."}
            
            return {"response": "No reconozco esa acción de sesión en Windows."}
        
        except Exception as e:
            return {"response": f"❌ Error al ejecutar comando: {e}"}
    
    def shutdown(self):
        pass
