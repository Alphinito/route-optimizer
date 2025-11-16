"""
Optimizador de Rutas de Entrega - Punto de entrada principal

Este script calcula la ruta óptima para realizar entregas en múltiples
domicilios partiendo desde un centro de distribución, utilizando algoritmos
de grafos en una red de carreteras representada como un grid.
"""

from src import Config, RoadGrid, GridRouteOptimizer, GridHTMLRenderer


def main():
    """Función principal del optimizador de rutas"""
    try:
        # Cargar configuración desde JSON
        config = Config("config.json")
        
        # Obtener parámetros del grid
        grid_config = config.get_grid_config()
        grid_width = grid_config.get("width", 15)
        grid_height = grid_config.get("height", 12)
        cell_size = grid_config.get("cell_size", 50)
        
        # Crear grid de carreteras
        road_grid = RoadGrid(grid_width, grid_height, cell_size)
        
        # Mapear puntos de interés (POIs) al grid
        for node in config.get_nodes():
            road_grid.add_poi(
                poi_id=node["id"],
                grid_x=node["grid_x"],
                grid_y=node["grid_y"]
            )
        
        # Obtener lista de domicilios a entregar
        delivery_addresses = config.get_delivery_addresses()
        if not delivery_addresses:
            print("⚠️  Error: No hay domicilios definidos en la configuración")
            return
        
        # Inicializar optimizador y calcular ruta
        optimizer = GridRouteOptimizer(road_grid)
        grid_route = optimizer.optimize_route(
            start_poi="distribution_center",
            destination_pois=delivery_addresses
        )
        
        # Generar visualización HTML
        renderer = GridHTMLRenderer(road_grid, config)
        renderer.render_route(grid_route, output_file="output.html")
        
        # Mostrar resultados
        _print_results(grid_route)
        
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo config.json")
    except KeyError as e:
        print(f"❌ Error de configuración: Falta la clave {e}")
    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def _print_results(grid_route):
    """Imprime los resultados de la optimización de forma legible"""
    print("\n" + "="*60)
    print("✅ OPTIMIZACIÓN COMPLETADA")
    print("="*60)
    print(f"📍 Ruta óptima: {' → '.join(grid_route.poi_path)}")
    print(f"🛣️  Intersecciones recorridas: {len(grid_route.path)}")
    print(f"📏 Distancia total: {grid_route.total_distance:.2f} px")
    print(f"📄 Archivo generado: output.html")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
