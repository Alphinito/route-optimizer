from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
import heapq

@dataclass
class Node:
    """Representa un nodo en el grafo (domicilio o centro de distribución)"""
    id: str
    name: str
    x: float  # Coordenada X para renderización
    y: float  # Coordenada Y para renderización
    node_type: str  # "distribution_center", "delivery", etc.

@dataclass
class Edge:
    """Representa una arista (carretera) entre dos nodos"""
    from_node: str
    to_node: str
    distance: float
    is_blocked: bool = False
    road_id: str = None

class Graph:
    """Grafo ponderado para representar la red de carreteras"""
    
    def __init__(self, config):
        self.config = config
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[Tuple[str, str], Edge] = {}
        self._load_graph_from_config(config)
    
    def _load_graph_from_config(self, config):
        """Carga nodos y aristas desde la configuración"""
        # Cargar nodos
        for node_data in config.get_nodes():
            node = Node(
                id=node_data["id"],
                name=node_data["name"],
                x=node_data["x"],
                y=node_data["y"],
                node_type=node_data["type"]
            )
            self.nodes[node.id] = node
        
        # Cargar aristas
        for edge_data in config.get_edges():
            edge = Edge(
                from_node=edge_data["from"],
                to_node=edge_data["to"],
                distance=edge_data["distance"],
                is_blocked=edge_data.get("is_blocked", False),
                road_id=edge_data.get("road_id")
            )
            key = (edge.from_node, edge.to_node)
            self.edges[key] = edge
            
            # Agregar arista bidireccional si no es dirigida
            if not edge_data.get("directed", False):
                reverse_edge = Edge(
                    from_node=edge.to_node,
                    to_node=edge.from_node,
                    distance=edge.distance,
                    is_blocked=edge.is_blocked,
                    road_id=edge.road_id
                )
                reverse_key = (edge.to_node, edge.from_node)
                self.edges[reverse_key] = reverse_edge
    
    def get_neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        """Obtiene vecinos accesibles de un nodo (excluyendo bloqueados)"""
        neighbors = []
        for (from_node, to_node), edge in self.edges.items():
            if from_node == node_id and not edge.is_blocked:
                neighbors.append((to_node, edge.distance))
        return neighbors
    
    def get_edge(self, from_node: str, to_node: str) -> Edge:
        """Obtiene una arista específica"""
        return self.edges.get((from_node, to_node))
    
    def get_path_edges(self, path: List[str]) -> List[Edge]:
        """Obtiene todas las aristas que componen una ruta"""
        edges = []
        for i in range(len(path) - 1):
            edge = self.get_edge(path[i], path[i + 1])
            if edge:
                edges.append(edge)
        return edges
    
    def block_road(self, road_id: str):
        """Bloquea todas las aristas asociadas con un road_id"""
        for edge in self.edges.values():
            if edge.road_id == road_id:
                edge.is_blocked = True
    
    def unblock_road(self, road_id: str):
        """Desbloquea todas las aristas asociadas con un road_id"""
        for edge in self.edges.values():
            if edge.road_id == road_id:
                edge.is_blocked = False
