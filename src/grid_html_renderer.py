from typing import List, Tuple, Optional
from src.optimization_strategies import OptimizedRoute

class GridHTMLRenderer:
    """Renderizador HTML mejorado para grid de carreteras"""
    
    def __init__(self, road_grid, config):
        self.road_grid = road_grid
        self.config = config
    
    def render_route(self, grid_route: OptimizedRoute, output_file: str = "output.html") -> None:
        """Renderiza la ruta en un archivo HTML"""
        html_content = self._generate_html(grid_route, None)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def render_comparison(self, primary_route: OptimizedRoute, secondary_route: OptimizedRoute, 
                         output_file: str = "output.html") -> None:
        """Renderiza dos rutas para comparación"""
        html_content = self._generate_html(primary_route, secondary_route)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html(self, primary_route: OptimizedRoute, secondary_route: Optional[OptimizedRoute] = None) -> str:
        """Genera contenido HTML con una o dos rutas"""
        css = self._generate_css()
        
        min_x, min_y, max_x, max_y = self.road_grid.get_grid_bounds()
        viewbox = f"{min_x} {min_y} {max_x} {max_y}"
        
        # Canvas primario
        canvas_primary = self._generate_canvas(primary_route, is_secondary=False)
        
        # Canvas secundario (si existe)
        canvas_secondary = ""
        secondary_section = ""
        if secondary_route:
            canvas_secondary = self._generate_canvas(secondary_route, is_secondary=True)
            secondary_section = self._generate_secondary_section(secondary_route, viewbox, canvas_secondary)
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ruta de Entrega Optimizada - Grid Avanzado</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚚 Ruta de Entrega Optimizada</h1>
        
        {self._generate_primary_section(primary_route, viewbox, canvas_primary)}
        
        {secondary_section}
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #ddd;"></div>
                <span>Carreteras disponibles</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #3498db;"></div>
                <span>Ruta óptima</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #e74c3c;"></div>
                <span>Centro de distribución</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #27ae60;"></div>
                <span>Domicilios</span>
            </div>
        </div>
    </div>
</body>
</html>"""
        return html
    
    def _generate_primary_section(self, grid_route, viewbox: str, canvas: str) -> str:
        """Genera la sección primaria con la primera ruta"""
        poi_sequence = " → ".join(grid_route.path)
        intersection_count = len(grid_route.full_path)
        
        return f"""        <div class="route-section primary-section">
            <h2>📍 Ruta Inicial</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h3>📊 Estadísticas</h3>
                    <p><strong>Algoritmo:</strong> {grid_route.algorithm_name}</p>
                    <p><strong>Distancia Total:</strong> {grid_route.total_distance:.2f} px</p>
                    <p><strong>Intersecciones:</strong> {intersection_count}</p>
                    <p><strong>Domicilios:</strong> {len(grid_route.path) - 1}</p>
                </div>
                <div class="info-card">
                    <h3>🗺️ Ruta</h3>
                    <p><strong>Secuencia:</strong></p>
                    <p class="route-sequence">{poi_sequence}</p>
                </div>
                <div class="info-card">
                    <h3>✅ Algoritmos Utilizados</h3>
                    <p><strong>Dijkstra:</strong> Camino más corto</p>
                    <p><strong>TSP:</strong> Vecino más cercano</p>
                </div>
            </div>
            <div class="map-container">
                <svg class="map" viewBox="{viewbox}">
                    {canvas}
                </svg>
            </div>
        </div>"""
    
    def _generate_secondary_section(self, grid_route, viewbox: str, canvas: str) -> str:
        """Genera la sección secundaria con la ruta optimizada"""
        poi_sequence = " → ".join(grid_route.path)
        intersection_count = len(grid_route.full_path)
        
        return f"""        <div class="comparison-divider"></div>
        
        <div class="route-section secondary-section">
            <h2>🚀 Ruta Optimizada</h2>
            <div class="info-grid">
                <div class="info-card highlight">
                    <h3>📊 Estadísticas</h3>
                    <p><strong>Algoritmo:</strong> {grid_route.algorithm_name}</p>
                    <p><strong>Distancia Total:</strong> {grid_route.total_distance:.2f} px</p>
                    <p><strong>Intersecciones:</strong> {intersection_count}</p>
                    <p><strong>Domicilios:</strong> {len(grid_route.path) - 1}</p>
                    {f'<p><strong>Iteraciones 2-Opt:</strong> {grid_route.iterations}</p>' if grid_route.iterations > 0 else ''}
                </div>
                <div class="info-card">
                    <h3>🗺️ Ruta</h3>
                    <p><strong>Secuencia:</strong></p>
                    <p class="route-sequence">{poi_sequence}</p>
                </div>
                <div class="info-card">
                    <h3>✅ Algoritmos Utilizados</h3>
                    <p><strong>Dijkstra:</strong> Camino más corto</p>
                    <p><strong>TSP + 2-Opt:</strong> Optimización local</p>
                </div>
            </div>
            <div class="map-container">
                <svg class="map" viewBox="{viewbox}">
                    {canvas}
                </svg>
            </div>
        </div>"""
    
    def _generate_css(self) -> str:
        """Genera CSS para estilos"""
        return """        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            color: #333;
            margin-bottom: 20px;
            text-align: center;
            font-size: 2.5em;
        }
        
        h2 {
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            font-size: 1.8em;
        }
        
        .route-section {
            margin-bottom: 30px;
        }
        
        .primary-section {
            background: #f0f4f8;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #3498db;
        }
        
        .secondary-section {
            background: #f0f8f4;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #27ae60;
        }
        
        .comparison-divider {
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            margin: 30px 0;
            border-radius: 2px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .info-card {
            background: white;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .info-card.highlight {
            background: linear-gradient(135deg, #e8f8f5 0%, #d5f4e6 100%);
            border-left: 4px solid #27ae60;
        }
        
        .info-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .secondary-section .info-card h3 {
            color: #27ae60;
        }
        
        .info-card p {
            margin: 5px 0;
            color: #555;
            font-size: 14px;
        }
        
        .route-sequence {
            color: #333;
            font-size: 13px;
            word-break: break-word;
            font-weight: bold;
        }
        
        .map-container {
            position: relative;
            width: 100%;
            margin-bottom: 20px;
            border: 2px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background: #f5f7fa;
        }
        
        .map {
            width: 100%;
            height: 600px;
            display: block;
        }
        
        .grid-line {
            stroke: #e0e0e0;
            stroke-width: 0.5;
        }
        
        .road {
            stroke: #bbb;
            stroke-width: 2;
            fill: none;
        }
        
        .road-blocked {
            stroke: #ff4444;
            stroke-width: 3;
            stroke-dasharray: 4,4;
            opacity: 1;
        }
        
        .route-road {
            stroke: #3498db;
            stroke-width: 3;
            fill: none;
            opacity: 0.9;
            stroke-linecap: round;
            stroke-linejoin: round;
        }
        
        .route-road.secondary {
            stroke: #3498db;
        }
        
        .intersection {
            fill: #f5f7fa;
            stroke: #999;
            stroke-width: 1;
        }
        
        .intersection-active {
            fill: #e8f4f8;
            stroke: #3498db;
            stroke-width: 2;
        }
        
        .intersection-active.secondary {
            fill: #e8f4f8;
            stroke: #3498db;
        }
        
        .poi-marker {
            fill: #e74c3c;
            stroke: #c0392b;
            stroke-width: 2;
        }
        
        .poi-marker.delivery {
            fill: #27ae60;
            stroke: #229954;
        }
        
        .poi-label {
            font-size: 12px;
            fill: #333;
            text-anchor: middle;
            font-weight: bold;
            pointer-events: none;
        }
        
        .route-highlight {
            stroke: #3498db;
            stroke-width: 3;
            fill: none;
            opacity: 0.8;
            animation: pulse 2s infinite;
            stroke-linecap: round;
            stroke-linejoin: round;
        }
        
        @keyframes pulse {
            0%, 100% { stroke-width: 3; opacity: 0.8; }
            50% { stroke-width: 4; opacity: 1; }
        }
        
        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
            margin-top: 20px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }
        
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 2px;
            border: 1px solid #999;
        }"""
    
    def _generate_canvas(self, grid_route, is_secondary: bool = False) -> str:
        """Genera elementos SVG del mapa del grid"""
        elements = []
        route_path_set = set(grid_route.full_path)
        route_edges = set()
        
        # Construir conjunto de aristas en la ruta usando full_path (intersecciones)
        for i in range(len(grid_route.full_path) - 1):
            route_edges.add((grid_route.full_path[i], grid_route.full_path[i + 1]))
            route_edges.add((grid_route.full_path[i + 1], grid_route.full_path[i]))
        
        # Dibujar carreteras normales primero (fondo)
        for (from_id, to_id), road in self.road_grid.roads.items():
            if to_id > from_id:  # Evitar duplicados
                from_intersection = road.from_intersection
                to_intersection = road.to_intersection
                
                # Solo dibujar carreteras NO bloqueadas aquí
                if road.is_passable:
                    is_in_route = (from_id, to_id) in route_edges
                    class_attr = "route-road" if is_in_route else "road"
                    
                    if is_secondary and is_in_route:
                        class_attr += " secondary"
                    
                    line = f'''            <line x1="{from_intersection.pixel_x}" y1="{from_intersection.pixel_y}"
                       x2="{to_intersection.pixel_x}" y2="{to_intersection.pixel_y}"
                       class="{class_attr}"/>'''
                    elements.append(line)
        
        # Dibujar carreteras bloqueadas DESPUÉS (superpuesta, siempre visible)
        for (from_id, to_id), road in self.road_grid.roads.items():
            if to_id > from_id:  # Evitar duplicados
                if not road.is_passable:  # Solo las bloqueadas
                    from_intersection = road.from_intersection
                    to_intersection = road.to_intersection
                    
                    line = f'''            <line x1="{from_intersection.pixel_x}" y1="{from_intersection.pixel_y}"
                       x2="{to_intersection.pixel_x}" y2="{to_intersection.pixel_y}"
                       class="road-blocked"/>'''
                    elements.append(line)
        
        # Dibujar intersecciones
        for intersection in self.road_grid.intersections.values():
            if intersection.is_passable:
                class_attr = "intersection-active" if intersection.intersection_id in route_path_set else "intersection"
                
                if is_secondary and intersection.intersection_id in route_path_set:
                    class_attr += " secondary"
                
                circle = f'''            <circle cx="{intersection.pixel_x}" cy="{intersection.pixel_y}" r="3"
                    class="{class_attr}"/>'''
                elements.append(circle)
        
        # Dibujar POIs
        for poi_id, intersection_id in self.road_grid.poi_map.items():
            intersection = self.road_grid.intersections.get(intersection_id)
            if intersection:
                # Obtener tipo de POI
                node_data = next((n for n in self.config.get_nodes() if n["id"] == poi_id), None)
                node_type = node_data["type"] if node_data else "delivery"
                
                poi_class = "poi-marker"
                if node_type != "distribution_center":
                    poi_class += " delivery"
                
                # Obtener nombre corto
                name = node_data["name"] if node_data else poi_id
                
                circle = f'''            <circle cx="{intersection.pixel_x}" cy="{intersection.pixel_y}" r="8"
                    class="{poi_class}"/>
            <text x="{intersection.pixel_x}" y="{intersection.pixel_y + 18}" class="poi-label">{name}</text>'''
                elements.append(circle)
        
        return "\n".join(elements)
