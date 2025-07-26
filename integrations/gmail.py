# integrations/gmail.py - Integración MCP para Gmail

import json
import subprocess
import threading
from typing import List, Optional, Dict, Any
from integrations_manager import MCPIntegration

class GmailIntegration(MCPIntegration):
    """Integración con Gmail usando Model Context Protocol"""
    
    def __init__(self, name: str, config: dict = None):
        super().__init__(name, config)
        self.mcp_process = None
        self.connected = False
        
    def initialize(self) -> bool:
        """Inicializa la conexión MCP con Gmail"""
        try:
            print(f"🔧 Inicializando integración Gmail...")
            
            # Verificar credenciales
            credentials_path = self.config.get('mcp_server', {}).get('env', {}).get('GMAIL_CREDENTIALS')
            if not credentials_path:
                print("❌ No se configuraron credenciales de Gmail")
                return False
            
            # Conectar servidor MCP
            if self.connect_mcp_server():
                self.connected = True
                print("✅ Gmail MCP conectado")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error inicializando Gmail: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Capacidades de la integración Gmail"""
        return [
            "enviar correo",
            "leer correos",
            "buscar emails",
            "revisar bandeja",
            "email",
            "gmail",
            "correo electrónico"
        ]
    
    def handle_command(self, command: str, context: dict = None) -> Optional[Dict[str, Any]]:
        """Maneja comandos relacionados con Gmail"""
        if not self.connected:
            return {"response": "Gmail no está conectado. Revisa la configuración."}
        
        command_lower = command.lower()
        
        # Enviar correo
        if any(keyword in command_lower for keyword in ["enviar", "send", "mandar"]):
            return self._handle_send_email(command, context)
        
        # Leer correos
        elif any(keyword in command_lower for keyword in ["leer", "read", "revisar", "check"]):
            return self._handle_read_emails(command, context)
        
        # Buscar correos
        elif any(keyword in command_lower for keyword in ["buscar", "search", "encontrar"]):
            return self._handle_search_emails(command, context)
        
        return None
    
    def _handle_send_email(self, command: str, context: dict = None) -> Dict[str, Any]:
        """Maneja el envío de correos"""
        try:
            # Extraer información del comando
            # Por ahora una implementación básica
            response = "Para enviar un correo necesito más información:\n"
            response += "- Destinatario (¿a quién?)\n"
            response += "- Asunto (¿sobre qué?)\n"
            response += "- Mensaje (¿qué quieres decir?)"
            
            return {
                "response": response,
                "action": "request_email_details",
                "next_steps": ["recipient", "subject", "body"]
            }
            
        except Exception as e:
            return {"response": f"Error enviando correo: {e}"}
    
    def _handle_read_emails(self, command: str, context: dict = None) -> Dict[str, Any]:
        """Maneja la lectura de correos"""
        try:
            # Simular llamada MCP para obtener emails
            emails = self._get_recent_emails(limit=5)
            
            if not emails:
                return {"response": "No hay correos nuevos en tu bandeja de entrada."}
            
            response = f"Tienes {len(emails)} correos recientes:\n\n"
            for i, email in enumerate(emails, 1):
                response += f"{i}. De: {email['from']}\n"
                response += f"   Asunto: {email['subject']}\n"
                response += f"   Fecha: {email['date']}\n\n"
            
            return {"response": response, "action": "emails_listed", "emails": emails}
            
        except Exception as e:
            return {"response": f"Error leyendo correos: {e}"}
    
    def _handle_search_emails(self, command: str, context: dict = None) -> Dict[str, Any]:
        """Maneja la búsqueda de correos"""
        try:
            # Extraer términos de búsqueda del comando
            search_terms = self._extract_search_terms(command)
            
            if not search_terms:
                return {"response": "¿Qué quieres buscar en tus correos?"}
            
            # Simular búsqueda MCP
            results = self._search_emails(search_terms)
            
            if not results:
                return {"response": f"No encontré correos con '{search_terms}'"}
            
            response = f"Encontré {len(results)} correos sobre '{search_terms}':\n\n"
            for result in results[:3]:  # Mostrar solo los primeros 3
                response += f"• {result['subject']} - {result['from']}\n"
            
            return {"response": response, "action": "search_results", "results": results}
            
        except Exception as e:
            return {"response": f"Error buscando correos: {e}"}
    
    def _get_recent_emails(self, limit: int = 5) -> List[Dict]:
        """Obtiene correos recientes (simulado)"""
        # En implementación real, aquí harías la llamada MCP
        return [
            {
                "from": "ejemplo@email.com",
                "subject": "Reunión de mañana",
                "date": "2025-01-27 10:30",
                "id": "msg_001"
            },
            {
                "from": "noreply@github.com",
                "subject": "New pull request",
                "date": "2025-01-27 09:15",
                "id": "msg_002"
            }
        ]
    
    def _extract_search_terms(self, command: str) -> str:
        """Extrae términos de búsqueda del comando"""
        # Lógica básica para extraer términos
        words = command.lower().split()
        search_words = []
        
        skip_words = {"buscar", "search", "encontrar", "correos", "emails", "en", "mis"}
        
        for word in words:
            if word not in skip_words and len(word) > 2:
                search_words.append(word)
        
        return " ".join(search_words)
    
    def _search_emails(self, terms: str) -> List[Dict]:
        """Busca correos por términos (simulado)"""
        # En implementación real, aquí harías la llamada MCP
        return [
            {
                "from": "equipo@proyecto.com",
                "subject": f"Resultado de búsqueda: {terms}",
                "date": "2025-01-26 14:20",
                "id": "search_001"
            }
        ]
    
    def connect_mcp_server(self) -> bool:
        """Conecta con el servidor MCP de Gmail"""
        try:
            server_config = self.server_config
            command = server_config.get('command', 'python')
            args = server_config.get('args', [])
            env = server_config.get('env', {})
            
            # En implementación real, aquí iniciarías el proceso MCP
            print(f"🔗 Conectando MCP Gmail server: {command} {' '.join(args)}")
            
            # Simular conexión exitosa
            return True
            
        except Exception as e:
            print(f"❌ Error conectando MCP Gmail: {e}")
            return False
    
    def shutdown(self):
        """Cierra la conexión MCP"""
        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mcp_process.kill()
            except Exception as e:
                print(f"⚠️ Error cerrando proceso MCP Gmail: {e}")
        
        self.connected = False
        print("🔌 Gmail MCP desconectado")