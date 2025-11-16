"""
Módulo de estrategias de optimización de rutas.

Implementa diferentes algoritmos para optimizar rutas TSP:
- Heurística de vecino más cercano (base)
- 2-opt (local search - mejora rutas existentes)
- Genético (futuro)
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
import heapq
from abc import ABC, abstractmethod


@dataclass
class OptimizedRoute:
    """Representa una ruta optimizada con metadatos"""
    path: List[str]  # Lista de POI IDs en orden
    full_path: List[str]  # Ruta completa con todas las intersecciones
    total_distance: float
    algorithm_name: str
    iterations: int = 0  # Para 2-opt, cuántas iteraciones se realizaron


class OptimizationStrategy(ABC):
    """Clase base para estrategias de optimización"""
    
    def __init__(self, road_grid):
        self.road_grid = road_grid
    
    @abstractmethod
    def optimize(self, start_poi: str, destination_pois: List[str]) -> OptimizedRoute:
        """Implementa la estrategia de optimización"""
        pass
    
    def _solve_tsp_nearest_neighbor(self, start_poi: str, destination_pois: List[str],
                                    distance_matrix: Dict) -> List[str]:
        """TSP usando heurística de vecino más cercano"""
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
    
    def _dijkstra_distance(self, start_intersection: str, end_intersection: str) -> float:
        """Calcula la distancia mínima entre dos intersecciones"""
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
    
    def _calculate_poi_distance_matrix(self, pois: List[str]) -> Dict[Tuple[str, str], float]:
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
    
    def _build_full_path(self, poi_path: List[str]) -> List[str]:
        """Construye la ruta completa a través del grid"""
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
                full_path.extend(segment[1:])
        
        return full_path
    
    def _calculate_path_distance(self, poi_path: List[str]) -> float:
        """Calcula la distancia total de una ruta de POIs"""
        total = 0
        for i in range(len(poi_path) - 1):
            from_poi = poi_path[i]
            to_poi = poi_path[i + 1]
            total += self._dijkstra_distance(
                self.road_grid.get_poi_intersection(from_poi).intersection_id,
                self.road_grid.get_poi_intersection(to_poi).intersection_id
            )
        return total


class NearestNeighborStrategy(OptimizationStrategy):
    """Heurística de Vecino Más Cercano - Base"""
    
    def optimize(self, start_poi: str, destination_pois: List[str]) -> OptimizedRoute:
        """TSP usando vecino más cercano"""
        all_pois = [start_poi] + destination_pois
        distance_matrix = self._calculate_poi_distance_matrix(all_pois)
        
        # Resolver TSP
        poi_path = self._solve_tsp_nearest_neighbor(start_poi, destination_pois, distance_matrix)
        
        # Construir ruta completa
        full_path = self._build_full_path(poi_path)
        total_distance = self._calculate_path_distance(poi_path)
        
        return OptimizedRoute(
            path=poi_path,
            full_path=full_path,
            total_distance=total_distance,
            algorithm_name="TSP Nearest Neighbor"
        )


class TwoOptStrategy(OptimizationStrategy):
    """Nearest Neighbor + 2-Opt - Optimización local"""
    
    def __init__(self, road_grid, max_iterations: int = 1000):
        super().__init__(road_grid)
        self.max_iterations = max_iterations
    
    def optimize(self, start_poi: str, destination_pois: List[str]) -> OptimizedRoute:
        """TSP usando vecino más cercano + 2-opt"""
        all_pois = [start_poi] + destination_pois
        distance_matrix = self._calculate_poi_distance_matrix(all_pois)
        
        # Paso 1: Obtener ruta inicial con nearest neighbor
        poi_path = self._solve_tsp_nearest_neighbor(start_poi, destination_pois, distance_matrix)
        
        # Paso 2: Mejorar con 2-opt
        poi_path, iterations = self._two_opt(poi_path, distance_matrix)
        
        # Paso 3: Construir ruta completa
        full_path = self._build_full_path(poi_path)
        total_distance = self._calculate_path_distance(poi_path)
        
        return OptimizedRoute(
            path=poi_path,
            full_path=full_path,
            total_distance=total_distance,
            algorithm_name="TSP + 2-Opt Local Search",
            iterations=iterations
        )
    
    def _two_opt(self, route: List[str], distance_matrix: Dict) -> Tuple[List[str], int]:
        """
        Algoritmo 2-Opt: intercambia pares de aristas para reducir cruces
        
        Intenta revertir segmentos de la ruta para encontrar mejoras.
        Para cada par de posiciones (i, j), intenta revertir el segmento
        entre ellas y mantiene el cambio si mejora la distancia.
        """
        best_route = route[:]
        improved = True
        iteration = 0
        
        while improved and iteration < self.max_iterations:
            improved = False
            iteration += 1
            best_distance = self._calculate_route_distance(best_route, distance_matrix)
            
            # Intentar todos los posibles 2-opt swaps
            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route)):
                    if j - i == 1:
                        continue  # Saltar si son adyacentes
                    
                    # Crear nueva ruta invirtiendo segmento entre i y j
                    new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                    new_distance = self._calculate_route_distance(new_route, distance_matrix)
                    
                    # Si es mejor, actualizar
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
                        break  # Reintentar desde el inicio
                
                if improved:
                    break
        
        return best_route, iteration
    
    def _calculate_route_distance(self, route: List[str], distance_matrix: Dict) -> float:
        """Calcula la distancia total de una ruta"""
        total = 0
        for i in range(len(route) - 1):
            total += distance_matrix.get((route[i], route[i + 1]), float('inf'))
        return total


class OptimizationStrategyFactory:
    """Factory para crear estrategias de optimización"""
    
    _strategies = {
        "nearest_neighbor": NearestNeighborStrategy,
        "2opt": TwoOptStrategy,
    }
    
    @classmethod
    def create(cls, strategy_name: str, road_grid, **kwargs) -> OptimizationStrategy:
        """
        Crea una estrategia de optimización
        
        Args:
            strategy_name: Nombre de la estrategia ("nearest_neighbor", "2opt", etc.)
            road_grid: Instancia de RoadGrid
            **kwargs: Parámetros adicionales para la estrategia
        
        Returns:
            Instancia de OptimizationStrategy
        """
        if strategy_name not in cls._strategies:
            raise ValueError(f"Estrategia desconocida: {strategy_name}. "
                           f"Disponibles: {list(cls._strategies.keys())}")
        
        strategy_class = cls._strategies[strategy_name]
        return strategy_class(road_grid, **kwargs)
    
    @classmethod
    def register(cls, name: str, strategy_class: type):
        """Registra una nueva estrategia"""
        cls._strategies[name] = strategy_class
