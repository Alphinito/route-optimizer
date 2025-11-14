from typing import List, Tuple

class GridHTMLRenderer:
    """Renderizador HTML mejorado para grid de carreteras"""
    
    def __init__(self, road_grid, config):
        self.road_grid = road_grid
        self.config = config
    
    def render_route(self, grid_route, output_file: str = "output.html"):
        """Renderiza la ruta en un archivo HTML"""
        html_content = self._generate_html(grid_route)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html(self, grid_route) -> str:
        """Genera contenido HTML completo con grid mejorado"""
        css = self._generate_css()
        canvas = self._generate_canvas(grid_route)
        
        min_x, min_y, max_x, max_y = self.road_grid.get_grid_bounds()
        viewbox = f"{min_x} {min_y} {max_x} {max_y}"
        
        # Generar info de la ruta
        poi_sequence = " → ".join(grid_route.poi_path)
        intersection_count = len(grid_route.path)
        
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
        <div class="info-grid">
            <div class="info-card">
                <h3>📊 Estadísticas</h3>
                <p><strong>Distancia Total:</strong> {grid_route.total_distance:.2f} px</p>
                <p><strong>Intersecciones:</strong> {intersection_count}</p>
                <p><strong>Domicilios:</strong> {len(grid_route.poi_path) - 1}</p>
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
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .info-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 4px;
        }
        
        .info-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1em;
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
            stroke: #999;
            stroke-width: 2;
            fill: none;
        }
        
        .road-blocked {
            stroke: #ddd;
            stroke-dasharray: 5,5;
            opacity: 0.5;
        }
        
        .route-road {
            stroke: #3498db;
            stroke-width: 3;
            fill: none;
            opacity: 0.9;
            stroke-linecap: round;
            stroke-linejoin: round;
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
    
    def _generate_canvas(self, grid_route) -> str:
        """Genera elementos SVG del mapa del grid"""
        elements = []
        route_path_set = set(grid_route.path)
        route_edges = set()
        
        # Construir conjunto de aristas en la ruta
        for i in range(len(grid_route.path) - 1):
            route_edges.add((grid_route.path[i], grid_route.path[i + 1]))
            route_edges.add((grid_route.path[i + 1], grid_route.path[i]))
        
        # Dibujar todas las carreteras primero (fondo)
        for (from_id, to_id), road in self.road_grid.roads.items():
            if to_id > from_id:  # Evitar duplicados
                from_intersection = road.from_intersection
                to_intersection = road.to_intersection
                
                is_in_route = (from_id, to_id) in route_edges
                class_attr = "route-road" if is_in_route else "road"
                
                if not road.is_passable:
                    class_attr += " road-blocked"
                
                line = f'''            <line x1="{from_intersection.pixel_x}" y1="{from_intersection.pixel_y}"
                   x2="{to_intersection.pixel_x}" y2="{to_intersection.pixel_y}"
                   class="{class_attr}"/>'''
                elements.append(line)
        
        # Dibujar intersecciones
        for intersection in self.road_grid.intersections.values():
            if intersection.is_passable:
                class_attr = "intersection-active" if intersection.intersection_id in route_path_set else "intersection"
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
