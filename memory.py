# memory.py - Versión básica funcional

class Memory:
    def __init__(self):
        self.entries = []
        self.corrections = {}
        
    def size(self):
        """Devuelve el número de entradas en memoria"""
        return len(self.entries)
    
    def corrections_count(self):
        """Devuelve el número de correcciones"""
        return len(self.corrections)
    
    def add_entry(self, entry):
        """Añade una entrada a la memoria"""
        self.entries.append(entry)
    
    def get_context(self):
        """Devuelve el contexto de memoria como string"""
        if not self.entries:
            return ""
        
        # Devolver las últimas 5 entradas como contexto
        recent_entries = self.entries[-5:]
        return "\n".join([str(entry) for entry in recent_entries])
    
    def clear(self):
        """Limpia la memoria"""
        self.entries.clear()
        self.corrections.clear()