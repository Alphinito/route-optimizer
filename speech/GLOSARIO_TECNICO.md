# Glosario Técnico - Sistema de Optimización de Rutas de Entrega

## Conceptos Fundamentales

### **Grafo**
Estructura de datos compuesta por nodos (vértices) conectados mediante aristas (edges). En este sistema, el grafo representa la red de carreteras donde las intersecciones son nodos y las carreteras son aristas.

**Propiedades en nuestro sistema**:
- **No dirigido**: Puedes ir en ambas direcciones por una carretera
- **Conexo**: Existe camino entre cualquier par de intersecciones
- **Ponderado**: Cada arista tiene un peso (distancia euclidiana)
- **Planar**: Puede dibujarse en 2D sin cruzamientos

---

### **Nodo (Node/Vertex)**
Un punto en el grafo. En este sistema hay dos tipos:
- **Intersección**: Puntos de cruce de carreteras en el grid (identificadas como `grid_X_Y`)
- **POI**: Punto de Interés mapeado a una intersección

---

### **Arista (Edge)**
Conexión entre dos nodos. En este sistema representa una carretera bidireccional entre dos intersecciones adyacentes.

**Propiedades**:
- **Identificador**: Tupla `(from_id, to_id)` ej: `("grid_5_3", "grid_6_3")`
- **Peso**: Distancia euclidiana en píxeles entre nodos
- **Estado**: `is_passable` (accesible o bloqueada)

---

### **Peso (Weight)**
Valor numérico asignado a una arista que representa el "costo" de atravesarla. En este sistema es la **distancia euclidiana** en píxeles.

```
Fórmula: √[(px1 - px2)² + (py1 - py2)²]
Ejemplo: distance("grid_5_3" → "grid_6_3") = 45.0 px
```

---

## Abreviaciones y Acrónimos

### **POI**
**Point Of Interest** (Punto de Interés)

Ubicaciones específicas en el grid que representan:
- **Domicilios** (deliveries): Direcciones donde se deben entregar paquetes
- **Centro de Distribución** (distribution_center): Punto de partida de todas las rutas

**Representación**:
```json
{
  "id": "delivery_1",
  "name": "Dom. 1",
  "grid_x": 2,
  "grid_y": 2,
  "type": "delivery"
}
```

En el sistema se almacenan en `road_grid.poi_map`:
```python
poi_map["delivery_1"] = "grid_2_2"  # POI mapeado a intersección
```

---

### **TSP**
**Traveling Salesman Problem** (Problema del Viajante)

Problema clásico de optimización combinatoria: encontrar el orden de visita de múltiples destinos que minimice la distancia total.

**En nuestro sistema**:
- Destino: distribution_center
- Puntos a visitar: 15 domicilios
- Objetivo: Secuencia que minimice distancia total

**Complejidad**: O(n!) = O(15!) ≈ 1.3 billones de combinaciones posibles

---

### **NearestNeighbor / NN**
**Heurística del Vecino Más Cercano**

Algoritmo greedy simple para resolver TSP:
1. Comenzar en el punto inicial
2. Siempre visitar el punto no visitado más cercano
3. Repetir hasta visitar todos

**Complejidad**: O(n²) = O(256) operaciones (16 POIs)  
**Calidad**: 10-30% peor que óptimo típicamente  
**Ventaja**: Muy rápido, resultado razonable

---

### **2-Opt**
**Algoritmo de Intercambio Local de 2 Aristas**

Técnica de búsqueda local (local search) que mejora una ruta existente:
1. Tomar dos aristas no adyacentes en la ruta
2. Invertir el segmento entre ellas
3. Si la distancia mejora, mantener el cambio
4. Repetir hasta convergencia

**Concepto visual**:
```
Antes (cruces):          Después (2-Opt):
    A ─── B                  A ─── D
     \   /                    \   /
      \ /                      X (sin cruce)
       X                       / \
      / \                      B ─ C
     C ─ D
```

**Complejidad**: O(m × n³) donde m = iteraciones de mejora (típicamente 3-10)  
**Mejora esperada**: 5-20% de reducción adicional  
**Garantía**: Nunca empeora, converge a óptimo local

---

### **Dijkstra**
**Algoritmo de Dijkstra para Camino Más Corto**

Algoritmo fundamental que encuentra el camino de distancia mínima entre dos nodos en un grafo ponderado.

**Funcionamiento**:
1. Inicializar distancia a origen como 0, resto como ∞
2. Usar priority queue (heap) para procesar nodos por distancia
3. Para cada nodo, relajar (actualizar) distancias de vecinos
4. Continuar hasta visitarlos todos

**Complejidad**: O((V + E) log V) = O(9088) operaciones en nuestro grid  
**Garantía**: Óptimo (si todos los pesos son no-negativos)  
**Dos versiones**:
- `_dijkstra_distance()`: Retorna solo la distancia
- `_dijkstra_path()`: Retorna la secuencia de nodos

---

### **Dijkstra Distance**
Método que **solo calcula la distancia mínima** entre dos intersecciones.

```python
distance = dijkstra_distance("grid_10_6", "grid_2_2")  # Retorna: 360.0
```

**Uso**: Cuando solo necesitas saber qué tan lejos están dos puntos

---

### **Dijkstra Path**
Método que **retorna la secuencia completa de intersecciones** del camino más corto.

```python
path = dijkstra_path("grid_10_6", "grid_2_2")
# Retorna: ["grid_10_6", "grid_9_6", "grid_8_6", ..., "grid_2_2"]
```

**Uso**: Cuando necesitas saber exactamente por dónde pasa la ruta

---

## Estructuras de Datos

### **GridIntersection**
Representa una intersección (nodo) en el grid.

```python
@dataclass
class GridIntersection:
    grid_x: int              # Coordenada X en el grid (0-19)
    grid_y: int              # Coordenada Y en el grid (0-11)
    pixel_x: float           # Posición X en píxeles para renderizar
    pixel_y: float           # Posición Y en píxeles para renderizar
    is_passable: bool = True # ¿Se puede atravesar esta intersección?
    intersection_id: str     # Identificador único: "grid_X_Y"
```

**Ejemplo**:
```python
GridIntersection(
    grid_x=5,
    grid_y=3,
    pixel_x=247.5,           # 5*45 + 22.5
    pixel_y=157.5,           # 3*45 + 22.5
    is_passable=True,
    intersection_id="grid_5_3"
)
```

---

### **GridRoad**
Representa una carretera (arista) entre dos intersecciones.

```python
@dataclass
class GridRoad:
    from_intersection: GridIntersection    # Intersección de origen
    to_intersection: GridIntersection      # Intersección de destino
    is_passable: bool = True               # ¿Se puede usar esta carretera?
    road_segment_id: str                   # Identificador único
```

**Nota**: Cada carretera bidireccional se almacena como DOS aristas:
- `roads[("grid_5_3", "grid_6_3")]` = carretera de izquierda a derecha
- `roads[("grid_6_3", "grid_5_3")]` = carretera de derecha a izquierda

---

### **RoadGrid**
Grafo completo que representa toda la red de carreteras.

```python
class RoadGrid:
    grid_width: int = 20                              # 20 celdas de ancho
    grid_height: int = 12                             # 12 celdas de alto
    cell_size: float = 45                             # Tamaño de celda en píxeles
    intersections: Dict[str, GridIntersection]        # Todos los nodos: 240 total
    roads: Dict[Tuple[str, str], GridRoad]            # Todas las aristas: 896 total
    poi_map: Dict[str, str]                           # Mapeo POI → intersección
```

**Estadísticas**:
- Intersecciones: 20 × 12 = 240
- Carreteras (1 dirección): 228 (horizontal) + 220 (vertical) = 448
- Carreteras (bidireccionales): 448 × 2 = 896 aristas

---

### **OptimizedRoute**
Resultado de la optimización: ruta completa con metadatos.

```python
@dataclass
class OptimizedRoute:
    path: List[str]              # Orden de POIs: ["dist_center", "del_2", "del_5", ...]
    full_path: List[str]         # Intersecciones completas: ["grid_10_6", "grid_9_6", ...]
    total_distance: float        # Distancia total en píxeles
    algorithm_name: str          # Nombre del algoritmo usado
    iterations: int = 0          # Para 2-opt: cuántas iteraciones de mejora
```

**Ejemplo**:
```python
OptimizedRoute(
    path=["distribution_center", "delivery_2", "delivery_5", ..., "delivery_15"],
    full_path=["grid_10_6", "grid_9_6", "grid_8_6", ..., "grid_2_2"],
    total_distance=3240.0,
    algorithm_name="TSP + 2-Opt Local Search",
    iterations=3
)
```

---

## Archivos y Módulos

### **main.py**
Archivo principal de entrada al sistema.

**Responsabilidades**:
1. Cargar configuración desde JSON
2. Crear el grid de carreteras
3. Mapear POIs
4. Aplicar bloqueos de carreteras
5. Ejecutar optimizadores
6. Renderizar output HTML

**Flujo**:
```python
config → RoadGrid → add_poi() → block_road() → optimize_route() → render_comparison()
```

---

### **config.py**
Módulo de gestión de configuración.

**Clase**: `Config`

**Métodos principales**:
- `get_grid_config()`: Retorna parámetros del grid
- `get_nodes()`: Retorna definición de todos los POIs
- `get_delivery_addresses()`: Retorna IDs de domicilios a entregar
- `get_blocked_roads()`: Retorna lista de carreteras bloqueadas

**Archivo de configuración**: `config.json`

---

### **grid_road.py**
Módulo de construcción del grafo de carreteras.

**Clases principales**:
- `Direction` (Enum): Direcciones posibles (NORTH, SOUTH, EAST, WEST, diagonales)
- `GridIntersection`: Nodo del grafo
- `GridRoad`: Arista del grafo
- `RoadGrid`: Grafo completo

**Métodos clave de RoadGrid**:
- `_create_grid()`: Inicializar todas las intersecciones y carreteras
- `add_poi()`: Mapear un POI a una intersección
- `get_neighbors()`: Obtener intersecciones adyacentes accesibles
- `block_road()`: Bloquear una carretera e intersección destino
- `unblock_road()`: Desbloquear una carretera e intersección
- `block_intersection()`: Bloquear una intersección específica

---

### **optimization_strategies.py**
Módulo de algoritmos de optimización.

**Clases principales**:
- `OptimizationStrategy` (ABC): Clase base abstracta
- `NearestNeighborStrategy`: Implementa heurística del vecino más cercano
- `TwoOptStrategy`: Implementa nearest neighbor + 2-opt
- `OptimizationStrategyFactory`: Factory para crear estrategias

**Métodos principales**:
- `_dijkstra_distance()`: Calcula distancia mínima entre dos nodos
- `_dijkstra_path()`: Calcula secuencia de nodos del camino mínimo
- `_calculate_poi_distance_matrix()`: Construye matriz de distancias entre POIs
- `_solve_tsp_nearest_neighbor()`: Resuelve TSP con heurística greedy
- `_two_opt()`: Mejora ruta con algoritmo 2-opt
- `_calculate_path_distance()`: Calcula distancia total de una ruta

---

### **grid_html_renderer.py**
Módulo de generación de visualización HTML.

**Clase**: `GridHTMLRenderer`

**Métodos principales**:
- `render_route()`: Renderiza una única ruta
- `render_comparison()`: Renderiza dos rutas para comparación
- `_generate_html()`: Genera contenido HTML completo
- `_generate_css()`: Genera estilos CSS
- `_generate_canvas()`: Genera elementos SVG del mapa

**Salida**: Archivo `output.html` con visualización interactiva

---

## Tipos de Datos y Enumeraciones

### **Direction (Enum)**
Enumeración de direcciones en el grid.

```python
class Direction(Enum):
    NORTH = (0, -1)       # Arriba
    SOUTH = (0, 1)        # Abajo
    EAST = (1, 0)         # Derecha
    WEST = (-1, 0)        # Izquierda
    NORTHEAST = (1, -1)   # Diagonal superior-derecha
    NORTHWEST = (-1, -1)  # Diagonal superior-izquierda
    SOUTHEAST = (1, 1)    # Diagonal inferior-derecha
    SOUTHWEST = (-1, 1)   # Diagonal inferior-izquierda
```

**Nota**: Actualmente no se usa en el código, pero está disponible para futuras extensiones.

---

## Conceptos de Optimización

### **Heurística**
Algoritmo aproximado que sacrifica optimalidad por velocidad.

**En nuestro sistema**:
- **Vecino Más Cercano**: Heurística constructiva (construye solución desde cero)
- **2-Opt**: Heurística de mejora (mejora solución existente)

**Ventajas**: Rápido, resultado razonable  
**Desventajas**: No garantiza solución óptima

---

### **Óptimo Global**
La mejor solución posible entre todas las alternativas.

**En TSP**: La ruta más corta de todas las 15! = 1.3 billones de combinaciones posibles  
**Complejidad**: O(n!) imposible de calcular en tiempo práctico

---

### **Óptimo Local**
La mejor solución en un vecindario pequeño.

**En 2-Opt**: No se puede mejorar invirtiendo ningún par de segmentos  
**Garantía**: 2-Opt siempre converge a óptimo local  
**Limitación**: Puede estar 5-20% alejado del óptimo global

---

### **Convergencia**
Proceso de aproximarse a una solución final.

**En 2-Opt**:
1. Iteración 1: Mejora encontrada → improved = True → continuar
2. Iteración 2: Mejora encontrada → improved = True → continuar
3. Iteración N: No se encuentra mejora → improved = False → terminar

**Criterio de parada**:
- Ninguna mejora detectada en una iteración completa, O
- Se alcanzó número máximo de iteraciones (1000)

---

### **Búsqueda Local (Local Search)**
Técnica que mejora una solución modificando pequeños elementos.

**Ejemplos**:
- **2-Opt**: Invierte segmentos de la ruta
- **3-Opt**: Invierte tres segmentos (más potente, más lento)
- **Lin-Kernighan**: Intercambia múltiples aristas (muy complejo)

**Ventaja**: Desde cualquier punto, puede mejorarse a óptimo local  
**Aplicación**: Comúnmente usado DESPUÉS de heurística constructiva

---

### **Relajación de Aristas**
Proceso de Dijkstra donde se actualiza la distancia a un vecino si se encuentra camino más corto.

```python
new_distance = current_distance + edge_distance

if new_distance < distances[neighbor]:
    distances[neighbor] = new_distance  # ← RELAJACIÓN
    heapq.heappush(pq, (new_distance, neighbor))
```

**Concepto**: "Relajar" el tensión en la distancia estimada si se encuentra evidencia de camino más corto

---

### **Priority Queue (Heap)**
Estructura de datos que siempre expone el elemento de menor prioridad.

**En Dijkstra**:
```python
import heapq

pq = []  # Priority queue
heapq.heappush(pq, (distance, node))      # Agregar elemento
distance, node = heapq.heappop(pq)        # Obtener mínimo
```

**Complejidad**:
- Push: O(log n)
- Pop: O(log n)
- En Dijkstra: O((V + E) log V)

---

## Conceptos de Red Vial

### **Grid**
Malla rectangular que representa el plano.

**En nuestro sistema**:
- Ancho: 20 celdas
- Alto: 12 celdas
- Tamaño de celda: 45 píxeles
- Total: 20 × 12 = 240 intersecciones

**Coordenadas**:
- Grid: (0-19, 0-11) coordenadas discretas
- Píxeles: (0-900, 0-540) coordenadas continuas

---

### **Intersección**
Punto en el grid donde se cruzan carreteras.

**Identificación**: `grid_X_Y` donde X ∈ [0, 19] y Y ∈ [0, 11]

**Ejemplo**: `grid_5_3` es la intersección en la columna 5, fila 3

**Propiedades**:
- Coordenadas en el grid
- Coordenadas en píxeles (para renderizar)
- Estado de accesibilidad (`is_passable`)

---

### **Carretera**
Conexión entre dos intersecciones adyacentes.

**Tipos**:
- **Horizontal**: Conecta `grid_X_Y` con `grid_(X+1)_Y`
- **Vertical**: Conecta `grid_X_Y` con `grid_X_(Y+1)`

**Bidireccionalidad**: Cada carretera se puede recorrer en ambas direcciones

**Estado**: Puede estar bloqueada (`is_passable=False`)

---

### **Bloqueo de Carreteras**
Marcar una carretera como no transitable.

**Implementación**:
```python
block_road("grid_10_1", "grid_10_2")
```

**Efectos**:
1. Marca `roads[("grid_10_1", "grid_10_2")].is_passable = False`
2. Marca `roads[("grid_10_2", "grid_10_1")].is_passable = False` (ambas direcciones)
3. Marca `intersections["grid_10_2"].is_passable = False` (previene cruces perpendiculares)

**Uso**: Simular construcciones, accidentes, o restricciones de tráfico

---

### **Línea de Bloqueo**
Múltiples carreteras bloqueadas formando una línea (vertical u horizontal).

**Ejemplo vertical** (x=10):
```python
blocked_roads = [
    ["grid_10_1", "grid_10_2"],
    ["grid_10_2", "grid_10_3"],
    ["grid_10_3", "grid_10_4"]
]
```

**Efecto**: Las rutas NO pueden cruzar la línea x=10 en ninguna dirección

---

## Recursos y Librerías

### **Python Standard Library**

- **json**: Lectura y parsing de `config.json`
- **heapq**: Priority queue para Dijkstra
- **typing**: Type hints (Dict, List, Tuple, Optional)
- **dataclasses**: Decorador @dataclass para estructuras
- **enum**: Enumeraciones (Direction)
- **abc**: Abstract Base Classes para OptimizationStrategy

---

### **Tipos Genéricos (Type Hints)**

```python
Dict[str, int]                    # Diccionario string → int
List[str]                         # Lista de strings
Tuple[str, float]                 # Tupla (string, float)
Optional[GridIntersection]        # GridIntersection o None
Dict[Tuple[str, str], float]      # Dict (tupla de 2 strings) → float (matriz de distancias)
```

---

## Medidas y Unidades

### **Distancia**
- **Unidad**: Píxeles (px)
- **Cálculo**: Distancia euclidiana en píxeles
- **Ejemplo**: Distancia entre `grid_5_3` y `grid_6_3` = 45.0 px

---

### **Iteraciones (en 2-Opt)**
- **Unidad**: Número de ciclos completos
- **Significado**: Cuántas veces se pasó sobre todos los pares de segmentos
- **Ejemplo**: 3 iteraciones significa 3 mejoras exitosas encontradas

---

### **Complejidad**

#### Notación Big O
- **O(1)**: Constante
- **O(n)**: Lineal
- **O(n²)**: Cuadrática
- **O(n³)**: Cúbica
- **O(n!)**: Factorial (combinaciones totales)
- **O((V+E) log V)**: Dijkstra típico

---

## Mejoras y Métricas de Calidad

### **Porcentaje de Mejora**
```
mejora = (distancia_inicial - distancia_optimizada) / distancia_inicial * 100
```

**En nuestro sistema**:
- Nearest Neighbor: 3780 px
- Después de 2-Opt: 3240 px
- **Mejora**: (3780 - 3240) / 3780 * 100 = 14.29%

---

### **Distancia Ahorrada**
```
ahorro = distancia_inicial - distancia_optimizada
```

**En nuestro sistema**: 3780 - 3240 = 540 px

---

## Referencias Cruzadas

### **Algoritmo → Archivo → Método**

| Algoritmo | Archivo | Clase | Método |
|-----------|---------|-------|--------|
| Dijkstra Distance | optimization_strategies.py | OptimizationStrategy | `_dijkstra_distance()` |
| Dijkstra Path | optimization_strategies.py | OptimizationStrategy | `_dijkstra_path()` |
| Nearest Neighbor | optimization_strategies.py | NearestNeighborStrategy | `_solve_tsp_nearest_neighbor()` |
| 2-Opt | optimization_strategies.py | TwoOptStrategy | `_two_opt()` |
| Grid Init | grid_road.py | RoadGrid | `_create_grid()` |
| Bloqueos | grid_road.py | RoadGrid | `block_road()` |
| Renderizado | grid_html_renderer.py | GridHTMLRenderer | `_generate_canvas()` |

---

## Ejemplos Prácticos Rápidos

### **Crear POI**
```python
# Config
config = Config("config.json")

# Grid
road_grid = RoadGrid(20, 12, 45)

# Agregar POI
road_grid.add_poi("delivery_1", 2, 2)
# → Resulta: poi_map["delivery_1"] = "grid_2_2"
```

---

### **Bloquear Carretera**
```python
# Bloquear una carretera vertical
road_grid.block_road("grid_10_1", "grid_10_2")

# Efecto:
# - roads[("grid_10_1", "grid_10_2")].is_passable = False
# - roads[("grid_10_2", "grid_10_1")].is_passable = False
# - intersections["grid_10_2"].is_passable = False
```

---

### **Calcular Distancia**
```python
from src.optimization_strategies import NearestNeighborStrategy

optimizer = NearestNeighborStrategy(road_grid)

# Distancia mínima entre dos intersecciones
distance = optimizer._dijkstra_distance("grid_10_6", "grid_2_2")
# Resultado: 360.0 px
```

---

### **Calcular Camino Completo**
```python
# Secuencia de intersecciones
path = optimizer._dijkstra_path("grid_10_6", "grid_2_2")
# Resultado: ["grid_10_6", "grid_9_6", "grid_8_6", ..., "grid_2_2"]
```

---

### **Optimizar Ruta**
```python
# Crear optimizador
optimizer = GridRouteOptimizer(road_grid)

# Generar ruta optimizada
route = optimizer.optimize_route(
    start_poi="distribution_center",
    destination_pois=["delivery_1", "delivery_2", ..., "delivery_15"],
    strategy="2opt"
)

# Resultado
print(route.path)              # Orden de visita
print(route.total_distance)    # 3240.0 px
print(route.iterations)        # 3 iteraciones de mejora
```

---

## Matriz de Comparación de Algoritmos

| Propiedad | Dijkstra | Nearest Neighbor | 2-Opt |
|-----------|----------|------------------|-------|
| **Propósito** | Camino más corto | Heurística TSP | Mejora local |
| **Garantía** | Óptimo global | No | Óptimo local |
| **Complejidad** | O((V+E) log V) | O(n²) | O(m × n³) |
| **Tiempo práctico** | 0-5ms | 10-20ms | 1-5ms |
| **Mejora esperada** | N/A (base) | N/A | 5-20% |
| **Usado para** | Camino entre POIs | Orden inicial | Refinar orden |
| **Se ejecuta primero** | Sí (dentro de NN) | Sí | Después de NN |

---

## Notas de Implementación

### **Por qué se bloquea la intersección destino?**
Cuando bloqueamos una carretera A→B, también bloqueamos la intersección B. Esto previene que rutas crucen perpendicularmente a través de B, lo que sería evitar el bloqueo.

**Ejemplo**:
```
Si solo bloqueamos carretera grid_10_4 → grid_10_5:
┌─────────────────────┐
│ X X X X X X X X X X │  ← Ruta podría cruzar aquí horizontalmente
│ grid_10_1 grid_10_2 │     atravesando grid_10_5
│ grid_10_3 grid_10_4 │  ← Carretera bloqueada
│ grid_10_5 grid_10_6 │  ← Sin bloqueo de intersección
│ X X X X X X X X X X │  ← Ruta podría cruzar aquí también
└─────────────────────┘

Con bloqueo de intersección grid_10_5:
┌─────────────────────┐
│ Ruta debe rodear    │  ← No puede pasar por grid_10_5
│ grid_10_1 grid_10_2 │
│ grid_10_3 grid_10_4 │  ← Carretera bloqueada
│ ✗ grid_10_5✗ 10_6  │  ← Intersección bloqueada
│ Ruta debe rodear    │  ← No puede pasar por grid_10_5
└─────────────────────┘
```

---

## Próximas Mejoras Potenciales

### **Algoritmos avanzados a implementar**
- **3-Opt**: Como 2-Opt pero invierte 3 segmentos (más potente)
- **Lin-Kernighan**: Algoritmo muy sofisticado de búsqueda local
- **Simulated Annealing**: Permite aceptar soluciones peores temporalmente
- **Algoritmo Genético**: Evoluciona población de soluciones

### **Optimizaciones técnicas**
- **Caché de distancias**: Almacenar matriz de distancias en disco
- **Paralelización**: Ejecutar Dijkstra en paralelo para múltiples POIs
- **Preprocesamiento**: Detectar subproblemas independientes

---

## Conclusión Rápida

Este glosario define todos los términos técnicos, abreviaciones y conceptos necesarios para entender el sistema de optimización de rutas. Use como referencia rápida mientras estudia el código y el `GUION_TECNICO_DETALLADO.md`.
