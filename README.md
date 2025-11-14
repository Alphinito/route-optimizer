# 🚚 Optimizador de Rutas de Entrega

Sistema inteligente para optimizar rutas de entrega usando **algoritmos de grafos** y **grid de carreteras complejas**. Calcula el camino más eficiente desde un centro de distribución hacia múltiples domicilios, considerando la red real de carreteras.

## ✨ Características

- **Grafo de Grid Complejo**: Representa una red realista de carreteras con intersecciones
- **Algoritmo de Dijkstra**: Encuentra el camino más corto entre intersecciones
- **Problema del Vendedor Viajero (TSP)**: Optimiza el orden de visita de domicilios con heurística de vecino más cercano
- **Visualización Interactiva**: Genera HTML con SVG mostrando:
  - Grid completo de carreteras
  - Ruta óptima destacada en azul
  - Centro de distribución y domicilios georreferenciados
  - Estadísticas detalladas

- **Arquitectura Extensible**:
  - Bloqueo/desbloqueo dinámico de carreteras
  - Configuración en JSON fácil de modificar
  - Separación clara de responsabilidades

## 🏗️ Arquitectura

### Estructura del Proyecto

```
final_project/
├── main.py                      # Punto de entrada
├── config.json                  # Configuración del grid y POIs
├── requirements.txt             # Dependencias
├── src/
│   ├── __init__.py
│   ├── config.py               # Gestión de configuración
│   ├── grid_road.py            # Modelo de grid de carreteras
│   ├── grid_route_optimizer.py # Optimizador de rutas
│   ├── grid_html_renderer.py   # Renderizador HTML/SVG
│   ├── graph.py                # Grafo original (deprecado)
│   ├── route_optimizer.py      # Optimizador original (deprecado)
│   └── html_renderer.py        # Renderizador original (deprecado)
└── .gitignore
```

### Componentes Principales

#### `RoadGrid` - Modelo de carreteras
- Crea un grid de intersecciones
- Conecta intersecciones adyacentes con carreteras
- Permite mapear POIs (puntos de interés) a intersecciones
- Soporta bloqueo/desbloqueo de carreteras

```python
road_grid = RoadGrid(width=15, height=12, cell_size=50)
road_grid.add_poi("delivery_1", grid_x=2, grid_y=2)
```

#### `GridRouteOptimizer` - Optimización de rutas
- Implementa Dijkstra para caminos más cortos
- Resuelve TSP aproximado con heurística de vecino más cercano
- Construye ruta completa a través del grid

```python
optimizer = GridRouteOptimizer(road_grid)
route = optimizer.optimize_route(
    start_poi="distribution_center",
    destination_pois=["delivery_1", "delivery_2", "delivery_3"]
)
```

#### `GridHTMLRenderer` - Visualización
- Genera SVG con el grid de carreteras
- Destaca la ruta óptima
- Incluye información de estadísticas

## 🚀 Instalación y Uso

### Requisitos
- Python 3.8+
- pip

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/yourusername/route-optimizer.git
cd route-optimizer
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

### Uso

1. **Configurar grid y POIs** en `config.json`:
```json
{
  "grid": {
    "width": 15,
    "height": 12,
    "cell_size": 50,
    "blocked_roads": []
  },
  "nodes": [
    {
      "id": "distribution_center",
      "name": "Centro Distribución",
      "grid_x": 7,
      "grid_y": 6,
      "type": "distribution_center"
    },
    {
      "id": "delivery_1",
      "name": "Dom. 1",
      "grid_x": 2,
      "grid_y": 2,
      "type": "delivery"
    }
  ],
  "delivery_addresses": ["delivery_1", "delivery_2"]
}
```

2. **Ejecutar el optimizador**
```bash
python main.py
```

3. **Ver resultado** en `output.html`
```bash
open output.html  # En macOS
start output.html  # En Windows
```

## 📊 Ejemplo de Salida

```
Ruta óptima: distribution_center → delivery_2 → delivery_4 → delivery_3 → delivery_1
Intersecciones recorridas: 38
Distancia total: 1850.00 px
Archivo generado: output.html
```

## 🔄 Algoritmos Implementados

### Algoritmo de Dijkstra
- **Complejidad**: O((V + E) log V)
- **Propósito**: Encontrar el camino más corto entre dos intersecciones
- **Implementación**: Usando cola de prioridad (heapq)

```python
def _dijkstra_distance(self, start: str, end: str) -> float:
    distances = {node: float('inf') for node in nodes}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        # ... procesar vecinos ...
    
    return distances[end]
```

### Problema del Vendedor Viajero (TSP) - Heurística de Vecino Más Cercano
- **Complejidad**: O(n²)
- **Propósito**: Optimizar el orden de visita de múltiples destinos
- **Aproximación**: ~125% del óptimo (suficiente para aplicaciones reales)

```python
def _solve_tsp_nearest_neighbor(self, start, destinations, matrix):
    path = [start]
    current = start
    unvisited = set(destinations)
    
    while unvisited:
        nearest = min(unvisited, key=lambda d: matrix[(current, d)])
        path.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    return path
```

## 🛣️ Estructura del Grid

El grid se organiza como una matriz de intersecciones:
- Cada intersección es un nodo del grafo
- Carreteras conectan intersecciones adyacentes (H/V)
- POIs (puntos de interés) se mapean a intersecciones

```
15 x 12 grid @ 50px por celda = 750 x 600 px
```

## 🔧 Extensibilidad

### Bloquear una carretera (construcción, etc.)
```python
road_grid.block_road("grid_5_5", "grid_6_5")
route = optimizer.optimize_route(...)  # Evitará esta carretera
```

### Bloquear una intersección
```python
road_grid.block_intersection("grid_5_5")
```

### Agregar más POIs
```python
road_grid.add_poi("delivery_5", grid_x=8, grid_y=10)
new_destinations = delivery_addresses + ["delivery_5"]
route = optimizer.optimize_route(..., destination_pois=new_destinations)
```

## 📈 Casos de Uso

- **Optimización de logística**: Calcular rutas eficientes de entrega
- **Planificación urbana**: Simular tráfico y rutas óptimas
- **Servicios de emergencia**: Encontrar rutas rápidas ignorando vías bloqueadas
- **Videojuegos**: Pathfinding en mapas con grid

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

## 📝 Notas Técnicas

### Por qué Grid en lugar de Grafo Arbitrario?
- **Realismo**: Simula carreteras reales en una ciudad
- **Rendimiento**: Grid permite optimizaciones (A*, distancia heurística)
- **Visualización**: SVG es perfecto para grids
- **Escalabilidad**: Fácil de ampliar con más intersecciones

### Limitaciones Actuales
- Solo conecta intersecciones adyacentes (H/V)
- No incluye diagonales (fácil de agregar)
- No simula tráfico en tiempo real
- POIs se fijan en intersecciones (no en puntos intermedios)

### Mejoras Futuras
- [ ] Agregar diagonales al grid
- [ ] Algoritmo A* para búsqueda más rápida
- [ ] Soporte para carreteras de acceso directo
- [ ] Matriz de tráfico con pesos dinámicos
- [ ] Interfaz web interactiva
- [ ] API REST

## 📄 Licencia

MIT License - Ver `LICENSE` para detalles

## 👨‍💻 Autor

Ángel - [GitHub](https://github.com/yourusername)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios mayores, abre un issue primero.

```bash
git clone <repository>
cd route-optimizer
git checkout -b feature/nueva-feature
# ... hacer cambios ...
git commit -am "Add nueva-feature"
git push origin feature/nueva-feature
```

## 📞 Soporte

Para reportar issues o sugerencias: [GitHub Issues](https://github.com/yourusername/route-optimizer/issues)

---

**Made with ❤️ by Ángel**
