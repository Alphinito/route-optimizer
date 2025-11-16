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
  - **2-Opt Local Search**: Mejora iterativa de rutas existentes (reduce distancia 15-30%)

- **Visualización Interactiva**: Genera HTML con SVG mostrando:
  - Grid completo de carreteras
  - Ruta óptima destacada en azul con animación
  - Centro de distribución y domicilios georreferenciados
  - Estadísticas detalladas (distancia, intersecciones, secuencia)
  - **NUEVO**: Comparación lado a lado de dos estrategias de optimización

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
    ├── grid_route_optimizer.py # Optimizador de rutas (interfaz)
    ├── grid_html_renderer.py   # Renderizador HTML/SVG
    └── optimization_strategies.py # Estrategias de optimización (NEW)
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
Calcula la ruta óptima usando algoritmos de grafos con soporte para múltiples estrategias.

```python
from src import GridRouteOptimizer

optimizer = GridRouteOptimizer(road_grid)

# Calcular ruta con vecino más cercano
route_nn = optimizer.optimize_route(
    start_poi="distribution_center",
    destination_pois=["delivery_1", "delivery_2", "delivery_3"],
    strategy="nearest_neighbor"  # por defecto
)

# Calcular ruta optimizada con 2-opt
route_2opt = optimizer.optimize_route(
    start_poi="distribution_center",
    destination_pois=["delivery_1", "delivery_2", "delivery_3"],
    strategy="2opt"
)

print(f"Ruta NN: {route_nn.total_distance:.2f} px")
print(f"Ruta 2-Opt: {route_2opt.total_distance:.2f} px")
print(f"Mejora: {(1 - route_2opt.total_distance/route_nn.total_distance)*100:.1f}%")
```

**Estrategias disponibles**:
- `"nearest_neighbor"`: Heurística rápida (O(n²))
- `"2opt"`: Optimización local iterativa (típicamente 15-30% mejora)

**Retorna**: `OptimizedRoute` con:
- `path`: Secuencia de POI IDs
- `full_path`: Todas las intersecciones del recorrido
- `total_distance`: Distancia total en píxeles
- `algorithm_name`: Nombre del algoritmo usado
- `iterations`: Número de iteraciones (para 2-opt)

#### `GridHTMLRenderer` - Visualización
Genera visualización interactiva en HTML/SVG con soporte para comparación de estrategias.

```python
from src import GridHTMLRenderer

renderer = GridHTMLRenderer(road_grid, config)

# Renderizar una única ruta
renderer.render_route(route, output_file="output.html")

# Renderizar comparación de dos rutas (NUEVO)
renderer.render_comparison(route_nn, route_2opt, output_file="output.html")
```

**Genera automáticamente**:
- Grid de carreteras en SVG con todas las intersecciones
- Ruta óptima destacada con colores diferenciados
- Posiciones de todos los POIs georreferenciados
- Panel de información con estadísticas
- **NUEVO**: Secciones lado a lado para comparación
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
======================================================================
✅ OPTIMIZACIÓN COMPLETADA - COMPARATIVA DE RESULTADOS
======================================================================

📍 RUTA INICIAL (Vecino más cercano):
   Secuencia: distribution_center → delivery_14 → delivery_2 → ...
   Intersecciones: 85
   Distancia: 3780.00 px

🚀 RUTA OPTIMIZADA (Vecino más cercano + 2-Opt):
   Secuencia: distribution_center → delivery_14 → delivery_2 → ...
   Intersecciones: 71
   Distancia: 3150.00 px
   Iteraciones 2-Opt: 5

📊 MEJORA: 16.67% reducción en distancia total
📏 Distancia ahorrada: 630.00 px

📄 Archivo generado: output.html
======================================================================
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
- **Usado por**: Todas las estrategias de optimización

### Problema del Vendedor Viajero (TSP) - Heurística de Vecino Más Cercano
- **Complejidad**: O(n²)
- **Propósito**: Optimizar el orden de visita de múltiples destinos
- **Aproximación**: ~125% del óptimo (suficiente para aplicaciones reales)
- **Ventajas**: Muy rápida, buena para problemas medianos

### Algoritmo 2-Opt (Local Search)
- **Complejidad**: O(n²) por iteración, típicamente converge en <100 iteraciones
- **Propósito**: Mejorar una ruta existente eliminando cruces (edge swaps)
- **Mejora observada**: 15-30% de reducción en distancia
- **Estrategia**: Aplicar después de vecino más cercano para refinar resultado
- **Ventajas**: Simple, efectivo, garantizado no empeorar la solución

**Cómo funciona 2-Opt**:
1. Comienza con una ruta inicial (p.ej., de vecino más cercano)
2. Busca pares de aristas que se cruzan en el mapa
3. "Invierte" el segmento entre ellas para eliminar el cruce
4. Si mejora, mantiene el cambio y repite
5. Termina cuando no encuentra mejoras o alcanza iteraciones máximas

```
Antes:     A ─→ B          Después:   A ─→ C
           ↖   ↙                      ↘   ↗
             X                          X
           ↗   ↖                      ↙   ↘
           C ─→ D                     B ─→ D
           
           (cruzadas)                 (sin cruzar)
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
