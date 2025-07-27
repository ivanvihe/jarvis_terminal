import os
import importlib
import json
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

class BaseIntegration(ABC):
    """Clase base para todas las integraciones"""
    
    def __init__(self, name: str, config: dict = None):
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Inicializa la integración. Retorna True si fue exitoso."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Retorna lista de capacidades que ofrece esta integración"""
        pass
    
    @abstractmethod
    def handle_command(self, command: str, context: dict = None) -> Optional[dict]:
        """
        Maneja un comando específico.
        Retorna None si no puede manejar el comando,
        o dict con 'response' y opcionalmente 'action'
        """
        pass
    
    def can_handle(self, command: str) -> bool:
        """Verifica si esta integración puede manejar el comando"""
        capabilities = self.get_capabilities()
        command_lower = command.lower()
        return any(cap.lower() in command_lower for cap in capabilities)
    
    def shutdown(self):
        """Limpieza al cerrar la integración"""
        pass

class MCPIntegration(BaseIntegration):
    """Integración específica para Model Context Protocol (MCP)"""
    
    def __init__(self, name: str, config: dict = None):
        super().__init__(name, config)
        self.mcp_client = None
        self.server_config = config.get('mcp_server', {})
    
    def connect_mcp_server(self) -> bool:
        """Conecta con el servidor MCP"""
        try:
            # Aquí iría la lógica para conectar con el servidor MCP
            # Por ahora simulamos la conexión
            print(f"🔗 Conectando MCP server para {self.name}...")
            return True
        except Exception as e:
            print(f"❌ Error conectando MCP {self.name}: {e}")
            return False

class IntegrationsManager:
    """Gestor principal de integraciones"""
    
    def __init__(self, config_path: str = "config.json"):
        self.integrations: Dict[str, BaseIntegration] = {}
        self.config_path = config_path
        self.integrations_config = {}
        self.load_config()
    
    def load_config(self):
        """Carga configuración de integraciones desde config.json"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.integrations_config = config.get('integrations', {})
        except Exception as e:
            print(f"⚠️ Error cargando config de integraciones: {e}")
            self.integrations_config = {}
    
    def discover_integrations(self, modules_dir: str = "integrations"):
        """Descubre automáticamente integraciones en el directorio"""
        if not os.path.exists(modules_dir):
            print(f"📁 Creando directorio {modules_dir}...")
            os.makedirs(modules_dir)
            return
        
        print(f"🔍 Buscando integraciones en {modules_dir}/...")
        
        for filename in os.listdir(modules_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                self.load_integration(module_name, modules_dir)
    
    def load_integration(self, module_name: str, modules_dir: str = "integrations"):
        """Carga una integración específica"""
        try:
            # Verificar si está habilitada en config
            integration_config = self.integrations_config.get(module_name, {})
            if not integration_config.get('enabled', True):
                print(f"⏸️ Integración {module_name} deshabilitada")
                return False
            
            # Importar módulo dinámicamente
            module_path = f"{modules_dir}.{module_name}"
            module = importlib.import_module(module_path)
            
            # Convertir nombre módulo a PascalCase para buscar clase
            integration_class_name = ''.join(word.capitalize() for word in module_name.split('_')) + 'Integration'
            integration_class = getattr(module, integration_class_name, None)
            
            if not integration_class:
                print(f"⚠️ No se encontró clase de integración '{integration_class_name}' en {module_name}")
                return False
            
            # Crear instancia
            integration = integration_class(module_name, integration_config)
            
            # Inicializar
            if integration.initialize():
                self.integrations[module_name] = integration
                capabilities = integration.get_capabilities()
                print(f"✅ Integración {module_name} cargada - Capacidades: {capabilities}")
                return True
            else:
                print(f"❌ Error inicializando {module_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error cargando integración {module_name}: {e}")
            return False
    
    def process_command(self, command: str, context: dict = None) -> Optional[dict]:
        """
        Procesa un comando a través de las integraciones disponibles
        Retorna la respuesta de la primera integración que pueda manejarlo
        """
        for name, integration in self.integrations.items():
            if integration.enabled and integration.can_handle(command):
                try:
                    result = integration.handle_command(command, context)
                    if result:
                        print(f"🎯 Comando manejado por integración: {name}")
                        return result
                except Exception as e:
                    print(f"❌ Error en integración {name}: {e}")
                    continue
        
        return None
    
    def get_available_integrations(self) -> List[str]:
        """Retorna lista de integraciones disponibles"""
        return list(self.integrations.keys())
    
    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """Retorna todas las capacidades por integración"""
        capabilities = {}
        for name, integration in self.integrations.items():
            if integration.enabled:
                capabilities[name] = integration.get_capabilities()
        return capabilities
    
    def enable_integration(self, name: str) -> bool:
        """Habilita una integración"""
        if name in self.integrations:
            self.integrations[name].enabled = True
            return True
        return False
    
    def disable_integration(self, name: str) -> bool:
        """Deshabilita una integración"""
        if name in self.integrations:
            self.integrations[name].enabled = False
            return True
        return False
    
    def reload_integration(self, name: str) -> bool:
        """Recarga una integración"""
        if name in self.integrations:
            self.integrations[name].shutdown()
            del self.integrations[name]
            return self.load_integration(name)
        return False
    
    def shutdown_all(self):
        """Cierra todas las integraciones"""
        for integration in self.integrations.values():
            try:
                integration.shutdown()
            except Exception as e:
                print(f"⚠️ Error cerrando integración: {e}")
        self.integrations.clear()

# Función de utilidad para Jarvis
def create_integrations_manager() -> IntegrationsManager:
    """Función de conveniencia para crear y configurar el gestor"""
    manager = IntegrationsManager()
    manager.discover_integrations()
    return manager
