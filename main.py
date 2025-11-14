from src.grid_road import RoadGrid
from src.grid_route_optimizer import GridRouteOptimizer
from src.grid_html_renderer import GridHTMLRenderer
from src.config import Config

def main():
    # Cargar configuración
    config = Config("config.json")
    
    # Obtener configuración del grid
    grid_config = config.get_grid_config()
    grid_width = grid_config.get("width", 15)
    grid_height = grid_config.get("height", 12)
    cell_size = grid_config.get("cell_size", 50)
    
    # Crear grid de carreteras
    road_grid = RoadGrid(grid_width, grid_height, cell_size)
    
    # Agregar puntos de interés (POIs)
    for node in config.get_nodes():
        road_grid.add_poi(
            node["id"],
            node["grid_x"],
            node["grid_y"]
        )
    
    # Inicializar optimizador de rutas
    optimizer = GridRouteOptimizer(road_grid)
    
    # Obtener lista de domicilios a entregar
    delivery_addresses = config.get_delivery_addresses()
    
    # Calcular ruta óptima
    grid_route = optimizer.optimize_route(
        start_poi="distribution_center",
        destination_pois=delivery_addresses
    )
    
    # Renderizar HTML con ruta destacada
    renderer = GridHTMLRenderer(road_grid, config)
    renderer.render_route(grid_route, output_file="output.html")
    
    print(f"Ruta óptima calculada: {grid_route.poi_path}")
    print(f"Intersecciones recorridas: {len(grid_route.path)}")
    print(f"Distancia total: {grid_route.total_distance:.2f} px")
    print("Archivo generado: output.html")

if __name__ == "__main__":
    main()
