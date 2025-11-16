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
        
        # Inicializar optimizador y calcular rutas
        optimizer = GridRouteOptimizer(road_grid)
        
        # Generar ruta con algoritmo de vecino más cercano
        route_nearest = optimizer.optimize_route(
            start_poi="distribution_center",
            destination_pois=delivery_addresses,
            strategy="nearest_neighbor"
        )
        
        # Generar ruta optimizada con 2-opt
        route_optimized = optimizer.optimize_route(
            start_poi="distribution_center",
            destination_pois=delivery_addresses,
            strategy="2opt"
        )
        
        # Generar visualización HTML con comparación
        renderer = GridHTMLRenderer(road_grid, config)
        renderer.render_comparison(route_nearest, route_optimized, output_file="output.html")
        
        # Mostrar resultados
        _print_results(route_nearest, route_optimized)
        
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo config.json")
    except KeyError as e:
        print(f"❌ Error de configuración: Falta la clave {e}")
    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def _print_results(route_nearest, route_optimized):
    """Imprime los resultados de la optimización de forma legible"""
    improvement = ((route_nearest.total_distance - route_optimized.total_distance) / 
                   route_nearest.total_distance * 100)
    
    print("\n" + "="*70)
    print("✅ OPTIMIZACIÓN COMPLETADA - COMPARATIVA DE RESULTADOS")
    print("="*70)
    
    print("\n📍 RUTA INICIAL (Vecino más cercano):")
    print(f"   Secuencia: {' → '.join(route_nearest.path[:10])}" + 
          ("..." if len(route_nearest.path) > 10 else ""))
    print(f"   Intersecciones: {len(route_nearest.full_path)}")
    print(f"   Distancia: {route_nearest.total_distance:.2f} px")
    
    print("\n🚀 RUTA OPTIMIZADA (Vecino más cercano + 2-Opt):")
    print(f"   Secuencia: {' → '.join(route_optimized.path[:10])}" + 
          ("..." if len(route_optimized.path) > 10 else ""))
    print(f"   Intersecciones: {len(route_optimized.full_path)}")
    print(f"   Distancia: {route_optimized.total_distance:.2f} px")
    print(f"   Iteraciones 2-Opt: {route_optimized.iterations}")
    
    print(f"\n📊 MEJORA: {improvement:.2f}% reducción en distancia total")
    print(f"📏 Distancia ahorrada: {route_nearest.total_distance - route_optimized.total_distance:.2f} px")
    print(f"\n📄 Archivo generado: output.html")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
