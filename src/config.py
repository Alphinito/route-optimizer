import json
from typing import List, Dict

class Config:
    """Gestiona la configuración de la aplicación"""
    
    def __init__(self, config_file: str):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def get_grid_config(self) -> Dict:
        """Obtiene configuración del grid"""
        return self.data.get("grid", {})
    
    def get_nodes(self) -> List[Dict]:
        """Obtiene lista de nodos"""
        return self.data.get("nodes", [])
    
    def get_edges(self) -> List[Dict]:
        """Obtiene lista de aristas (deprecado, usado para compatibilidad)"""
        return self.data.get("edges", [])
    
    def get_delivery_addresses(self) -> List[str]:
        """Obtiene lista de domicilios a entregar"""
        return self.data.get("delivery_addresses", [])
    
    def get_blocked_roads(self) -> List[str]:
        """Obtiene lista de carreteras bloqueadas"""
        return self.data.get("blocked_roads", [])
