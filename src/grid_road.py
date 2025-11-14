from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class Direction(Enum):
    """Direcciones posibles en el grid"""
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)
    NORTHEAST = (1, -1)
    NORTHWEST = (-1, -1)
    SOUTHEAST = (1, 1)
    SOUTHWEST = (-1, 1)

@dataclass
class GridIntersection:
    """Representa una intersección en el grid de carreteras"""
    grid_x: int
    grid_y: int
    pixel_x: float  # Coordenada en píxeles para renderización
    pixel_y: float
    is_passable: bool = True  # Para construcciones o bloqueos
    intersection_id: str = None
    
    def __post_init__(self):
        if self.intersection_id is None:
            self.intersection_id = f"grid_{self.grid_x}_{self.grid_y}"

@dataclass
class GridRoad:
    """Representa una carretera entre dos intersecciones en el grid"""
    from_intersection: GridIntersection
    to_intersection: GridIntersection
    is_passable: bool = True
    road_segment_id: str = None
    
    def __post_init__(self):
        if self.road_segment_id is None:
            self.road_segment_id = f"segment_{self.from_intersection.intersection_id}_{self.to_intersection.intersection_id}"

class RoadGrid:
    """Grafo de grid complejo que representa la red de carreteras con intersecciones"""
    
    def __init__(self, grid_width: int, grid_height: int, cell_size: float):
        """
        Inicializa el grid de carreteras
        
        Args:
            grid_width: Ancho del grid en celdas
            grid_height: Alto del grid en celdas
            cell_size: Tamaño de cada celda en píxeles
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.intersections: Dict[str, GridIntersection] = {}
        self.roads: Dict[Tuple[str, str], GridRoad] = {}
        self.poi_map: Dict[str, str] = {}  # Mapea POI a intersecciones
        
        self._create_grid()
    
    def _create_grid(self):
        """Crea el grid base de intersecciones"""
        # Primero crear todas las intersecciones
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                intersection = GridIntersection(
                    grid_x=x,
                    grid_y=y,
                    pixel_x=x * self.cell_size + self.cell_size / 2,
                    pixel_y=y * self.cell_size + self.cell_size / 2
                )
                self.intersections[intersection.intersection_id] = intersection
        
        # Luego crear las carreteras entre intersecciones
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                current_id = f"grid_{x}_{y}"
                current = self.intersections[current_id]
                
                # Crear carreteras horizontales
                if x < self.grid_width - 1:
                    right_id = f"grid_{x+1}_{y}"
                    right_intersection = self.intersections[right_id]
                    road = GridRoad(current, right_intersection)
                    self.roads[(current_id, right_id)] = road
                    # Carretera bidireccional
                    self.roads[(right_id, current_id)] = GridRoad(right_intersection, current)
                
                # Crear carreteras verticales
                if y < self.grid_height - 1:
                    down_id = f"grid_{x}_{y+1}"
                    down_intersection = self.intersections[down_id]
                    road = GridRoad(current, down_intersection)
                    self.roads[(current_id, down_id)] = road
                    # Carretera bidireccional
                    self.roads[(down_id, current_id)] = GridRoad(down_intersection, current)
    
    def add_poi(self, poi_id: str, grid_x: int, grid_y: int) -> str:
        """
        Agrega un punto de interés (domicilio, centro distribución) en una intersección
        
        Args:
            poi_id: Identificador único del POI
            grid_x: Coordenada X en el grid
            grid_y: Coordenada Y en el grid
            
        Returns:
            ID de la intersección asignada
        """
        grid_x = max(0, min(grid_x, self.grid_width - 1))
        grid_y = max(0, min(grid_y, self.grid_height - 1))
        
        intersection_id = f"grid_{grid_x}_{grid_y}"
        self.poi_map[poi_id] = intersection_id
        return intersection_id
    
    def get_poi_intersection(self, poi_id: str) -> Optional[GridIntersection]:
        """Obtiene la intersección asignada a un POI"""
        intersection_id = self.poi_map.get(poi_id)
        if intersection_id:
            return self.intersections.get(intersection_id)
        return None
    
    def get_neighbors(self, intersection_id: str) -> List[Tuple[str, float]]:
        """
        Obtiene intersecciones vecinas accesibles desde una intersección
        
        Returns:
            Lista de tuplas (intersection_id, distancia)
        """
        neighbors = []
        for (from_id, to_id), road in self.roads.items():
            if from_id == intersection_id and road.is_passable:
                # Calcular distancia euclidiana
                from_intersection = self.intersections[from_id]
                to_intersection = self.intersections[to_id]
                distance = ((from_intersection.pixel_x - to_intersection.pixel_x) ** 2 + 
                           (from_intersection.pixel_y - to_intersection.pixel_y) ** 2) ** 0.5
                neighbors.append((to_id, distance))
        return neighbors
    
    def block_road(self, from_id: str, to_id: str):
        """Bloquea una carretera específica"""
        key = (from_id, to_id)
        if key in self.roads:
            self.roads[key].is_passable = False
    
    def unblock_road(self, from_id: str, to_id: str):
        """Desbloquea una carretera específica"""
        key = (from_id, to_id)
        if key in self.roads:
            self.roads[key].is_passable = True
    
    def block_intersection(self, intersection_id: str):
        """Bloquea una intersección (construcción, etc.)"""
        if intersection_id in self.intersections:
            self.intersections[intersection_id].is_passable = False
    
    def unblock_intersection(self, intersection_id: str):
        """Desbloquea una intersección"""
        if intersection_id in self.intersections:
            self.intersections[intersection_id].is_passable = True
    
    def get_grid_bounds(self) -> Tuple[float, float, float, float]:
        """Retorna los límites del grid en píxeles (min_x, min_y, max_x, max_y)"""
        return (0, 0, self.grid_width * self.cell_size, self.grid_height * self.cell_size)
    
    def get_road(self, from_id: str, to_id: str) -> Optional[GridRoad]:
        """Obtiene una carretera específica"""
        return self.roads.get((from_id, to_id))
