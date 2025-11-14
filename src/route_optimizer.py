from typing import List, Dict
import heapq
from dataclasses import dataclass

@dataclass
class Route:
    """Representa una ruta óptima"""
    path: List[str]
    total_distance: float
    edges: List = None

class RouteOptimizer:
    """Optimizador de rutas usando algoritmos de grafos"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def optimize_route(self, start: str, destinations: List[str]) -> Route:
        """
        Calcula la ruta óptima desde un punto de partida hacia múltiples destinos.
        Usa heurística de vecino más cercano para TSP.
        """
        # Calcular matriz de distancias mínimas entre todos los puntos
        all_points = [start] + destinations
        distance_matrix = self._calculate_distance_matrix(all_points)
        
        # Resolver TSP aproximado
        optimal_path = self._solve_tsp_nearest_neighbor(start, destinations, distance_matrix)
        
        # Construir ruta completa con caminos reales
        full_path = self._build_full_path(optimal_path)
        total_distance = self._calculate_path_distance(full_path)
        
        edges = self.graph.get_path_edges(full_path)
        
        return Route(
            path=full_path,
            total_distance=total_distance,
            edges=edges
        )
    
    def _calculate_distance_matrix(self, nodes: List[str]) -> Dict[tuple, float]:
        """Calcula la matriz de distancias mínimas entre todos los nodos"""
        matrix = {}
        for i, from_node in enumerate(nodes):
            for to_node in nodes:
                if from_node != to_node:
                    distance = self._dijkstra_shortest_path(from_node, to_node)
                    matrix[(from_node, to_node)] = distance
        return matrix
    
    def _dijkstra_shortest_path(self, start: str, end: str) -> float:
        """
        Implementa algoritmo de Dijkstra para encontrar el camino más corto.
        Retorna la distancia mínima entre dos nodos.
        """
        distances = {node_id: float('inf') for node_id in self.graph.nodes}
        distances[start] = 0
        visited = set()
        pq = [(0, start)]
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            if current_node == end:
                return current_distance
            
            visited.add(current_node)
            
            for neighbor, edge_distance in self.graph.get_neighbors(current_node):
                if neighbor not in visited:
                    new_distance = current_distance + edge_distance
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        heapq.heappush(pq, (new_distance, neighbor))
        
        return distances[end]
    
    def _solve_tsp_nearest_neighbor(self, start: str, destinations: List[str], 
                                   distance_matrix: Dict) -> List[str]:
        """
        Resuelve TSP usando heurística de vecino más cercano.
        Aproximación rápida a O(n²).
        """
        unvisited = set(destinations)
        path = [start]
        current = start
        
        while unvisited:
            # Encontrar destino no visitado más cercano
            nearest = min(
                unvisited,
                key=lambda dest: distance_matrix.get((current, dest), float('inf'))
            )
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return path
    
    def _build_full_path(self, waypoints: List[str]) -> List[str]:
        """
        Construye la ruta completa con todos los nodos intermedios
        usando el camino más corto entre waypoints.
        """
        full_path = []
        for i in range(len(waypoints) - 1):
            segment = self._dijkstra_path(waypoints[i], waypoints[i + 1])
            if i == 0:
                full_path.extend(segment)
            else:
                full_path.extend(segment[1:])  # Evitar duplicados
        return full_path
    
    def _dijkstra_path(self, start: str, end: str) -> List[str]:
        """
        Retorna la secuencia de nodos del camino más corto.
        """
        distances = {node_id: float('inf') for node_id in self.graph.nodes}
        previous = {node_id: None for node_id in self.graph.nodes}
        distances[start] = 0
        visited = set()
        pq = [(0, start)]
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            for neighbor, edge_distance in self.graph.get_neighbors(current_node):
                if neighbor not in visited:
                    new_distance = current_distance + edge_distance
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current_node
                        heapq.heappush(pq, (new_distance, neighbor))
        
        # Reconstruir camino
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        return path[::-1]
    
    def _calculate_path_distance(self, path: List[str]) -> float:
        """Calcula la distancia total de una ruta"""
        total = 0
        for i in range(len(path) - 1):
            edge = self.graph.get_edge(path[i], path[i + 1])
            if edge and not edge.is_blocked:
                total += edge.distance
        return total
