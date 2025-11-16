"""
Módulo de optimización de rutas de entrega.

Contiene implementaciones de algoritmos de grafos para calcular
rutas óptimas en una red de carreteras representada como un grid.
"""

from .config import Config
from .grid_road import RoadGrid, GridIntersection, GridRoad
from .grid_route_optimizer import GridRouteOptimizer, GridRoute
from .grid_html_renderer import GridHTMLRenderer

__all__ = [
    "Config",
    "RoadGrid",
    "GridIntersection",
    "GridRoad",
    "GridRouteOptimizer",
    "GridRoute",
    "GridHTMLRenderer",
]

__version__ = "1.0.0"
