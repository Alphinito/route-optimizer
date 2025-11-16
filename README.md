# 🚚 Optimizador de Rutas de Entrega

Sistema inteligente para optimizar rutas de entrega usando **algoritmos de grafos** y **grid de carreteras complejas**. Calcula el camino más eficiente desde un centro de distribución hacia múltiples domicilios, considerando la red real de carreteras.

## ✨ Características

- **Grafo de Grid Complejo**: Representa una red realista de carreteras con intersecciones
  - Grid totalmente customizable (ancho, alto, tamaño de celda)
  - Cada intersección es un nodo del grafo
  - Las carreteras conectan intersecciones adyacentes

- **Algoritmos de Grafos Implementados**:
  - **Dijkstra**: Encuentra el camino más corto entre cualquier par de intersecciones
  - **TSP (Vecino Más Cercano)**: Optimiza el orden de visita de múltiples domicilios

- **Visualización Interactiva**: Genera HTML con SVG mostrando:
  - Grid completo de carreteras
  - Ruta óptima destacada en azul con animación
  - Centro de distribución y domicilios georreferenciados
  - Estadísticas detalladas (distancia, intersecciones, secuencia)

- **Totalmente Customizable**:
  - Configuración en JSON fácil de modificar
  - Parámetros del grid (ancho, alto, tamaño de celda)
  - Posiciones de puntos de interés (POIs)
  - Bloqueo/desbloqueo dinámico de carreteras
  - Listas de entregas configurables

- **Código Limpio y Mantenible**:
  - Separación clara de responsabilidades
  - Type hints y docstrings en todo el código
  - Manejo robusto de errores
  - Estructura modular con package proper

## 🏗️ Arquitectura

### Estructura del Proyecto

```
final_project/
├── main.py                      # Punto de entrada principal
├── config.json                  # Configuración del grid y POIs
├── requirements.txt             # Dependencias
├── PARAMETERS.md               # Guía completa de parámetros
│
└── src/                         # Módulo principal
    ├── __init__.py             # API pública del módulo
    ├── config.py               # Gestión de configuración
    ├── grid_road.py            # Modelo de grid de carreteras
    ├── grid_route_optimizer.py # Optimizador de rutas
    └── grid_html_renderer.py   # Renderizador HTML/SVG
```

### Componentes Principales

#### `RoadGrid` - Modelo de carreteras
Representa la red de carreteras como un grid de intersecciones conectadas.

```python
from src import RoadGrid

# Crear grid de 15x12 intersecciones, 50px entre cada una
road_grid = RoadGrid(width=15, height=12, cell_size=50)

# Mapear puntos de interés al grid
road_grid.add_poi("delivery_1", grid_x=2, grid_y=2)
road_grid.add_poi("distribution_center", grid_x=7, grid_y=6)

# Bloquear una carretera (construcción, etc.)
road_grid.block_road("grid_5_5", "grid_6_5")
```

**Características**:
- Crea automáticamente conexiones entre intersecciones adyacentes
- Permite mapear POIs a intersecciones específicas
- Soporta bloqueo/desbloqueo dinámico de carreteras
- Calcula vecinos accesibles para cada intersección

#### `GridRouteOptimizer` - Optimización de rutas
Calcula la ruta óptima usando algoritmos de grafos.

```python
from src import GridRouteOptimizer

optimizer = GridRouteOptimizer(road_grid)

# Calcular ruta óptima
route = optimizer.optimize_route(
    start_poi="distribution_center",
    destination_pois=["delivery_1", "delivery_2", "delivery_3"]
)

print(f"Ruta: {route.poi_path}")
print(f"Distancia: {route.total_distance:.2f} px")
print(f"Intersecciones recorridas: {len(route.path)}")
```

**Algoritmos implementados**:
- **Dijkstra**: O((V+E) log V) - Encuentra el camino más corto entre dos puntos
- **TSP Heurístico**: O(n²) - Ordena entregas usando la heurística de vecino más cercano

#### `GridHTMLRenderer` - Visualización
Genera visualización interactiva en HTML/SVG.

```python
from src import GridHTMLRenderer

renderer = GridHTMLRenderer(road_grid, config)
renderer.render_route(route, output_file="output.html")
```

**Genera automáticamente**:
- Grid de carreteras en SVG con todas las intersecciones
- Ruta óptima destacada en azul con animación pulsante
- Posiciones de todos los POIs georreferenciados
- Panel de información con estadísticas
- Leyenda de colores y elementos

#### `Config` - Gestión de configuración
Carga y valida configuración desde JSON con valores por defecto.

```python
from src import Config

config = Config("config.json")

# Acceso a configuración
grid_config = config.get_grid_config()  # {'width': 15, 'height': 12, 'cell_size': 50}
nodes = config.get_nodes()
deliveries = config.get_delivery_addresses()

# Búsqueda de nodos
node = config.get_node_by_id("delivery_1")
```

**Características**:
- Validación automática de campos requeridos
- Valores por defecto inteligentes
- Type hints en todos los métodos
- Docstrings en cada método
- Manejo robusto de errores

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

### Uso Rápido

```bash
python main.py
```

Esto cargará `config.json`, calculará la ruta óptima y generará `output.html`.

**Salida esperada**:
```
============================================================
✅ OPTIMIZACIÓN COMPLETADA
============================================================
📍 Ruta óptima: distribution_center → delivery_2 → delivery_4 → delivery_3 → delivery_1
🛣️  Intersecciones recorridas: 38
📏 Distancia total: 2035.00 px
📄 Archivo generado: output.html
============================================================
```

### Configuración

1. **Editar `config.json`** con tu grid y POIs:

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
    },
    {
      "id": "delivery_2",
      "name": "Dom. 2",
      "grid_x": 12,
      "grid_y": 3,
      "type": "delivery"
    }
  ],
  "delivery_addresses": [
    "delivery_1",
    "delivery_2"
  ]
}
```

2. **Ejecutar**:
```bash
python main.py
```

3. **Ver resultado**: Abre `output.html` en tu navegador

### Parámetros Customizables

Para una guía completa de parámetros customizables, consulta **[PARAMETERS.md](PARAMETERS.md)**

**Parámetros básicos del grid**:
- `width`: Número de intersecciones horizontales
- `height`: Número de intersecciones verticales
- `cell_size`: Distancia en píxeles entre intersecciones

**Parámetros de POI**:
- `id`: Identificador único
- `name`: Nombre legible
- `grid_x`: Posición horizontal (0 a width-1)
- `grid_y`: Posición vertical (0 a height-1)
- `type`: "distribution_center" o "delivery"

**Ejemplo: Grid más grande**
```json
{
  "grid": {
    "width": 30,
    "height": 25,
    "cell_size": 50
  },
  "nodes": [
    {
      "id": "distribution_center",
      "name": "Centro Distribución",
      "grid_x": 15,
      "grid_y": 12,
      "type": "distribution_center"
    },
    {
      "id": "delivery_1",
      "name": "Zona Norte",
      "grid_x": 8,
      "grid_y": 5,
      "type": "delivery"
    }
  ],
  "delivery_addresses": ["delivery_1"]
}
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
