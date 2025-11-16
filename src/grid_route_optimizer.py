from typing import List, Tuple
from src.optimization_strategies import OptimizationStrategyFactory, OptimizedRoute

class GridRouteOptimizer:
    """Optimizador de rutas para grid de carreteras"""
    
    def __init__(self, road_grid):
        self.road_grid = road_grid
        self.factory = OptimizationStrategyFactory()
    
    def optimize_route(self, start_poi: str, destination_pois: List[str], 
                      strategy: str = "nearest_neighbor") -> OptimizedRoute:
        """
        Calcula la ruta óptima desde un POI hacia múltiples destinos en el grid
        
        Args:
            start_poi: Punto de inicio (centro de distribución)
            destination_pois: Lista de destinos
            strategy: Nombre de la estrategia ("nearest_neighbor", "two_opt", etc)
        
        Returns:
            OptimizedRoute con la ruta calculada
        """
        strategy_instance = self.factory.create(strategy, self.road_grid)
        return strategy_instance.optimize(start_poi, destination_pois)
