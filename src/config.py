"""
Módulo de gestión de configuración.

Carga y valida la configuración del proyecto desde un archivo JSON,
incluyendo parámetros del grid y definición de puntos de interés.
"""

import json
from typing import List, Dict, Optional


class Config:
    """Gestor centralizado de configuración de la aplicación"""
    
    # Valores por defecto
    DEFAULT_GRID_WIDTH = 15
    DEFAULT_GRID_HEIGHT = 12
    DEFAULT_CELL_SIZE = 50
    
    def __init__(self, config_file: str):
        """
        Inicializa la configuración desde un archivo JSON
        
        Args:
            config_file: Ruta al archivo de configuración
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            json.JSONDecodeError: Si el JSON es inválido
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self._validate()
    
    def _validate(self) -> None:
        """Valida que la configuración tenga los campos requeridos"""
        if "nodes" not in self.data:
            raise KeyError("Campo requerido 'nodes' no encontrado en config.json")
        if "delivery_addresses" not in self.data:
            raise KeyError("Campo requerido 'delivery_addresses' no encontrado en config.json")
    
    def get_grid_config(self) -> Dict[str, int]:
        """
        Obtiene configuración del grid con valores por defecto
        
        Returns:
            Diccionario con parámetros: width, height, cell_size, blocked_roads
        """
        grid = self.data.get("grid", {})
        return {
            "width": grid.get("width", self.DEFAULT_GRID_WIDTH),
            "height": grid.get("height", self.DEFAULT_GRID_HEIGHT),
            "cell_size": grid.get("cell_size", self.DEFAULT_CELL_SIZE),
            "blocked_roads": grid.get("blocked_roads", []),
        }
    
    def get_nodes(self) -> List[Dict]:
        """
        Obtiene lista de nodos (POIs)
        
        Returns:
            Lista de diccionarios con definición de nodos
        """
        return self.data.get("nodes", [])
    
    def get_delivery_addresses(self) -> List[str]:
        """
        Obtiene lista de IDs de domicilios a entregar
        
        Returns:
            Lista de identificadores de domicilios
        """
        return self.data.get("delivery_addresses", [])
    
    def get_blocked_roads(self) -> List[str]:
        """
        Obtiene lista de carreteras bloqueadas desde grid.blocked_roads
        
        Returns:
            Lista de carreteras bloqueadas en formato [from_id, to_id]
        """
        grid_config = self.get_grid_config()
        return grid_config.get("blocked_roads", [])
    
    def get_node_by_id(self, node_id: str) -> Optional[Dict]:
        """
        Busca un nodo por su ID
        
        Args:
            node_id: Identificador del nodo
            
        Returns:
            Diccionario del nodo o None si no existe
        """
        for node in self.get_nodes():
            if node.get("id") == node_id:
                return node
        return None
