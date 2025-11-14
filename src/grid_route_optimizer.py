from typing import List, Tuple
import heapq
from dataclasses import dataclass

@dataclass
class GridRoute:
    """Representa una ruta óptima en el grid"""
    path: List[str]  # Lista de intersection_ids
    total_distance: float
    poi_path: List[str]  # Ruta de POI en orden de visita

class GridRouteOptimizer:
    """Optimizador de rutas para grid de carreteras"""
    
    def __init__(self, road_grid):
        self.road_grid = road_grid
    
    def optimize_route(self, start_poi: str, destination_pois: List[str]) -> GridRoute:
        """
        Calcula la ruta óptima desde un POI hacia múltiples destinos en el grid
        """
        # Obtener intersecciones correspondientes a los POIs
        start_intersection = self.road_grid.get_poi_intersection(start_poi)
        if not start_intersection:
            raise ValueError(f"POI {start_poi} no está mapeado a una intersección")
        
        # Calcular matriz de distancias entre todos los POIs
        all_pois = [start_poi] + destination_pois
        distance_matrix = self._calculate_poi_distance_matrix(all_pois)
        
        # Resolver TSP aproximado con heurística de vecino más cercano
        poi_path = self._solve_tsp_nearest_neighbor(start_poi, destination_pois, distance_matrix)
        
        # Construir la ruta completa a través del grid
        full_path = self._build_grid_path(poi_path)
        total_distance = self._calculate_path_distance(full_path)
        
        return GridRoute(
            path=full_path,
            total_distance=total_distance,
            poi_path=poi_path
        )
    
    def _calculate_poi_distance_matrix(self, pois: List[str]) -> dict:
        """Calcula matriz de distancias mínimas entre POIs"""
        matrix = {}
        for from_poi in pois:
            for to_poi in pois:
                if from_poi != to_poi:
                    from_intersection = self.road_grid.get_poi_intersection(from_poi)
                    to_intersection = self.road_grid.get_poi_intersection(to_poi)
                    if from_intersection and to_intersection:
                        distance = self._dijkstra_distance(
                            from_intersection.intersection_id,
                            to_intersection.intersection_id
                        )
                        matrix[(from_poi, to_poi)] = distance
        return matrix
    
    def _dijkstra_distance(self, start_intersection: str, end_intersection: str) -> float:
        """Calcula la distancia mínima entre dos intersecciones usando Dijkstra"""
        distances = {inter_id: float('inf') for inter_id in self.road_grid.intersections}
        distances[start_intersection] = 0
        visited = set()
        pq = [(0, start_intersection)]
        
        while pq:
            current_distance, current_intersection = heapq.heappop(pq)
            
            if current_intersection in visited:
                continue
            
            if current_intersection == end_intersection:
                return current_distance
            
            visited.add(current_intersection)
            
            for neighbor_id, edge_distance in self.road_grid.get_neighbors(current_intersection):
                if neighbor_id not in visited:
                    new_distance = current_distance + edge_distance
                    if new_distance < distances[neighbor_id]:
                        distances[neighbor_id] = new_distance
                        heapq.heappush(pq, (new_distance, neighbor_id))
        
        return distances[end_intersection]
    
    def _solve_tsp_nearest_neighbor(self, start_poi: str, destination_pois: List[str],
                                   distance_matrix: dict) -> List[str]:
        """Resuelve TSP usando heurística de vecino más cercano"""
        unvisited = set(destination_pois)
        path = [start_poi]
        current = start_poi
        
        while unvisited:
            nearest = min(
                unvisited,
                key=lambda dest: distance_matrix.get((current, dest), float('inf'))
            )
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return path
    
    def _build_grid_path(self, poi_path: List[str]) -> List[str]:
        """Construye la ruta completa a través del grid de intersecciones"""
        full_path = []
        
        for i in range(len(poi_path) - 1):
            from_poi = poi_path[i]
            to_poi = poi_path[i + 1]
            
            from_intersection = self.road_grid.get_poi_intersection(from_poi)
            to_intersection = self.road_grid.get_poi_intersection(to_poi)
            
            segment = self._dijkstra_path(
                from_intersection.intersection_id,
                to_intersection.intersection_id
            )
            
            if i == 0:
                full_path.extend(segment)
            else:
                full_path.extend(segment[1:])  # Evitar duplicados
        
        return full_path
    
    def _dijkstra_path(self, start_intersection: str, end_intersection: str) -> List[str]:
        """Retorna la secuencia de intersecciones del camino más corto"""
        distances = {inter_id: float('inf') for inter_id in self.road_grid.intersections}
        previous = {inter_id: None for inter_id in self.road_grid.intersections}
        distances[start_intersection] = 0
        visited = set()
        pq = [(0, start_intersection)]
        
        while pq:
            current_distance, current_intersection = heapq.heappop(pq)
            
            if current_intersection in visited:
                continue
            visited.add(current_intersection)
            
            for neighbor_id, edge_distance in self.road_grid.get_neighbors(current_intersection):
                if neighbor_id not in visited:
                    new_distance = current_distance + edge_distance
                    if new_distance < distances[neighbor_id]:
                        distances[neighbor_id] = new_distance
                        previous[neighbor_id] = current_intersection
                        heapq.heappush(pq, (new_distance, neighbor_id))
        
        # Reconstruir camino
        path = []
        current = end_intersection
        while current is not None:
            path.append(current)
            current = previous[current]
        return path[::-1]
    
    def _calculate_path_distance(self, path: List[str]) -> float:
        """Calcula la distancia total de una ruta"""
        total = 0
        for i in range(len(path) - 1):
            neighbors = self.road_grid.get_neighbors(path[i])
            for neighbor_id, distance in neighbors:
                if neighbor_id == path[i + 1]:
                    total += distance
                    break
        return total
