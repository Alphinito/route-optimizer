# Guión Técnico Detallado: Sistema de Optimización de Rutas de Entrega

## Tabla de Contenidos
1. [Introducción y Arquitectura General](#introducción-y-arquitectura-general)
2. [Flujo de Ejecución Principal](#flujo-de-ejecución-principal)
3. [Estructura del Grid como Grafo](#estructura-del-grid-como-grafo)
4. [Algoritmo Dijkstra](#algoritmo-dijkstra)
5. [Algoritmo TSP - Vecino Más Cercano](#algoritmo-tsp---vecino-más-cercano)
6. [Algoritmo 2-Opt](#algoritmo-2-opt)
7. [Iteración de Datos](#iteración-de-datos)
8. [Generación del Output HTML](#generación-del-output-html)

---

## Introducción y Arquitectura General

### Propósito del Sistema
Este sistema resuelve el **Problema del Viajante (TSP - Traveling Salesman Problem)** en un contexto real: encontrar la ruta óptima de entrega desde un centro de distribución a múltiples domicilios en una red de carreteras representada como un **grid bidimensional**.

### Conceptos Clave

#### 1. **Grid como Grafo**
El grid es un **grafo conexo no dirigido ponderado**:
- **Nodos**: Son las **intersecciones** del grid, identificadas como `grid_X_Y` donde X y Y son coordenadas del grid
- **Aristas**: Son las **carreteras** que conectan dos intersecciones adyacentes (horizontal o vertical)
- **Peso de aristas**: La distancia euclidiana en píxeles entre dos intersecciones
- **Bidireccionalidad**: Cada carretera física tiene dos direcciones representadas como dos aristas en el grafo

#### 2. **Puntos de Interés (POIs)**
Los POIs (domicilios y centro de distribución) se mapean a las intersecciones más cercanas del grid:
- Se almacenan en `road_grid.poi_map: Dict[str, str]` 
- La clave es el ID del POI (ej: `delivery_1`, `distribution_center`)
- El valor es el ID de la intersección (ej: `grid_2_3`)

#### 3. **Estructura de Datos Primaria**
La clase `RoadGrid` es el núcleo del sistema:
```
RoadGrid
├── grid_width: int = 20
├── grid_height: int = 12
├── cell_size: float = 45 (píxeles)
├── intersections: Dict[str, GridIntersection]
│   └── Key: "grid_X_Y", Value: GridIntersection(...)
├── roads: Dict[Tuple[str, str], GridRoad]
│   └── Key: ("grid_X_Y", "grid_X_Z"), Value: GridRoad(...)
└── poi_map: Dict[str, str]
    └── Key: "delivery_1", Value: "grid_2_3"
```

#### 4. **Tipos de Datos Fundamentales**

**GridIntersection** (dataclass):
```python
@dataclass
class GridIntersection:
    grid_x: int              # Coordenada X en el grid
    grid_y: int              # Coordenada Y en el grid
    pixel_x: float           # Posición X en píxeles (grid_x * cell_size + cell_size/2)
    pixel_y: float           # Posición Y en píxeles (grid_y * cell_size + cell_size/2)
    is_passable: bool = True # Accesibilidad (puede ser bloqueado)
    intersection_id: str     # "grid_X_Y"
```

**GridRoad** (dataclass):
```python
@dataclass
class GridRoad:
    from_intersection: GridIntersection
    to_intersection: GridIntersection
    is_passable: bool = True
    road_segment_id: str
```

**OptimizedRoute** (dataclass):
```python
@dataclass
class OptimizedRoute:
    path: List[str]          # Ruta de POIs: ["distribution_center", "delivery_1", "delivery_2", ...]
    full_path: List[str]     # Ruta completa: ["grid_10_6", "grid_9_6", "grid_8_6", ...]
    total_distance: float    # Distancia total en píxeles
    algorithm_name: str      # Nombre del algoritmo usado
    iterations: int = 0      # Para 2-opt, cuántas iteraciones se realizaron
```

#### 5. **Enumeración de Direcciones**
```python
class Direction(Enum):
    NORTH = (0, -1)      # Arriba
    SOUTH = (0, 1)       # Abajo
    EAST = (1, 0)        # Derecha
    WEST = (-1, 0)       # Izquierda
    NORTHEAST = (1, -1)  # Diagonales
    NORTHWEST = (-1, -1)
    SOUTHEAST = (1, 1)
    SOUTHWEST = (-1, 1)
```

---

## Flujo de Ejecución Principal

### Vista General del Flujo

```
main.py
    ↓
1. Cargar config.json (Config class)
    ↓
2. Crear RoadGrid (inicializar intersecciones y carreteras)
    ↓
3. Mapear POIs al grid (add_poi para cada nodo)
    ↓
4. Aplicar bloqueos de carreteras (block_road)
    ↓
5. Crear optimizador (GridRouteOptimizer)
    ↓
6. Generar ruta inicial (NearestNeighborStrategy)
    ↓
7. Generar ruta optimizada (TwoOptStrategy)
    ↓
8. Renderizar comparación HTML (GridHTMLRenderer)
    ↓
output.html
```

### Fase 1: Carga de Configuración

**Archivo**: `src/config.py`  
**Clase**: `Config`

```python
# Lectura del JSON
config = Config("config.json")
```

El archivo `config.json` tiene esta estructura:
```json
{
  "grid": {
    "width": 20,
    "height": 12,
    "cell_size": 45,
    "blocked_roads": [
      ["grid_10_1", "grid_10_2"],
      ["grid_10_2", "grid_10_3"]
    ]
  },
  "nodes": [
    {
      "id": "distribution_center",
      "grid_x": 10,
      "grid_y": 6
    },
    {
      "id": "delivery_1",
      "grid_x": 2,
      "grid_y": 2
    }
  ],
  "delivery_addresses": ["delivery_1", "delivery_2", ...]
}
```

**Métodos principales**:
- `get_grid_config()` → Devuelve `Dict[str, int]` con parámetros del grid
- `get_nodes()` → Devuelve `List[Dict]` con definición de todos los POIs
- `get_delivery_addresses()` → Devuelve `List[str]` con IDs de domicilios
- `get_blocked_roads()` → Devuelve `List[List[str]]` con carreteras bloqueadas

### Fase 2: Creación del Grid de Carreteras

**Archivo**: `src/grid_road.py`  
**Clase**: `RoadGrid`

```python
road_grid = RoadGrid(width=20, height=12, cell_size=45)
```

#### Proceso de Inicialización: `RoadGrid.__init__()` → `_create_grid()`

**Paso 1: Crear todas las intersecciones**
```
Para cada y desde 0 hasta grid_height-1:
    Para cada x desde 0 hasta grid_width-1:
        intersección_id = f"grid_{x}_{y}"
        pixel_x = x * cell_size + cell_size/2
        pixel_y = y * cell_size + cell_size/2
        
        Crear GridIntersection(
            grid_x=x,
            grid_y=y,
            pixel_x=pixel_x,
            pixel_y=pixel_y,
            is_passable=True,
            intersection_id=intersección_id
        )
        
        Almacenar en road_grid.intersections[intersección_id]
```

Para un grid 20×12, se crean **240 intersecciones**.

**Ejemplo de coordenadas**:
- Intersección `grid_0_0`: pixel_x=22.5, pixel_y=22.5
- Intersección `grid_5_3`: pixel_x=247.5, pixel_y=157.5 (asumiendo cell_size=45)

**Paso 2: Crear todas las carreteras (bidireccionales)**
```
Para cada intersección (x, y):
    
    SI x < grid_width - 1:
        Crear carretera horizontal derecha:
        (grid_x_y) → (grid_(x+1)_y)
        
        Crear carretera inversa bidireccional:
        (grid_(x+1)_y) → (grid_x_y)
    
    SI y < grid_height - 1:
        Crear carretera vertical abajo:
        (grid_x_y) → (grid_x_(y+1))
        
        Crear carretera inversa bidireccional:
        (grid_x_(y+1)) → (grid_x_y)
```

Para un grid 20×12:
- Carreteras horizontales: 19 × 12 = 228 (por dirección = 456)
- Carreteras verticales: 20 × 11 = 220 (por dirección = 440)
- Total de aristas: **896 carreteras bidireccionales**

Cada carretera almacena:
```python
roads[("grid_5_3", "grid_6_3")] = GridRoad(
    from_intersection=intersections["grid_5_3"],
    to_intersection=intersections["grid_6_3"],
    is_passable=True,
    road_segment_id="segment_grid_5_3_grid_6_3"
)
```

### Fase 3: Mapeo de POIs al Grid

**Archivo**: `src/grid_road.py`  
**Método**: `RoadGrid.add_poi(poi_id, grid_x, grid_y)`

```python
for node in config.get_nodes():
    road_grid.add_poi(
        poi_id=node["id"],          # "delivery_1"
        grid_x=node["grid_x"],       # 2
        grid_y=node["grid_y"]        # 2
    )
```

Cada POI se mapea a su intersección más cercana:
```python
road_grid.poi_map["delivery_1"] = "grid_2_2"
road_grid.poi_map["distribution_center"] = "grid_10_6"
```

El método `add_poi()` también valida límites (si grid_x > grid_width, se ajusta a grid_width-1).

### Fase 4: Aplicar Bloqueos de Carreteras

**Archivo**: `src/grid_road.py`  
**Método**: `RoadGrid.block_road(from_id, to_id)`

```python
blocked_roads = config.get_blocked_roads()
# blocked_roads = [["grid_10_1", "grid_10_2"], ["grid_10_2", "grid_10_3"], ...]

for blocked_road in blocked_roads:
    if isinstance(blocked_road, list) and len(blocked_road) == 2:
        road_grid.block_road(blocked_road[0], blocked_road[1])
```

**Proceso de bloqueo** (bidireccional):
```python
def block_road(self, from_id: str, to_id: str):
    # Paso 1: Marcar ambas direcciones de la carretera como no transitables
    if (from_id, to_id) in self.roads:
        self.roads[(from_id, to_id)].is_passable = False
    
    if (to_id, from_id) in self.roads:
        self.roads[(to_id, from_id)].is_passable = False
    
    # Paso 2: Bloquear la intersección destino para prevenir cruces perpendiculares
    self.block_intersection(to_id)
```

**¿Por qué bloquear la intersección destino?**
Si solo bloqueamos las carreteras pero no la intersección, una ruta podría cruzar perpendicularmente a través de esa intersección. Al bloquear la intersección (`is_passable=False`), el algoritmo Dijkstra la rechazará completamente.

**Ejemplo práctico**:
```
Si bloqueamos una línea vertical:
["grid_10_1", "grid_10_2"]  →  Bloquea carreteras y la intersección grid_10_2
["grid_10_2", "grid_10_3"]  →  Bloquea carreteras y la intersección grid_10_3

Resultado:
- Una ruta NO puede pasar por grid_10_2 ni grid_10_3
- Una ruta NO puede atravesar horizontalmente la zona x=10
```

---

## Estructura del Grid como Grafo

### Representación Matemática

El grid es un **grafo G = (V, E, w)** donde:

- **V** (Vértices) = {grid_0_0, grid_0_1, ..., grid_19_11} = 240 nodos
- **E** (Aristas) = {(u,v) : u y v son intersecciones adyacentes}
- **w** (Peso) = distancia euclidiana entre dos intersecciones

**Propiedades**:
- **No dirigido**: Si hay arista (u,v), hay arista (v,u)
- **Conexo**: Existe camino entre cualquier par de nodos (en el grid inicial sin bloqueos)
- **Ponderado**: Cada arista tiene peso (distancia)
- **Planar**: Puede dibujarse en 2D sin cruzamientos (solo visualmente representable)

### Relación Grafo-Grid

```
Posición (x,y) en el grid  →  Intersección "grid_x_y"
    ↓                              ↓
    Píxeles                    Vértice del grafo
    (x*45 + 22.5, y*45 + 22.5)     ↓
                            Punto en el plano 2D
```

### Cálculo de Pesos (Distancias)

La distancia entre dos intersecciones es **euclidiana**:

```python
distance = √[(px1 - px2)² + (py1 - py2)²]
```

Ejemplo:
```
grid_5_3: pixel_x = 5*45 + 22.5 = 247.5, pixel_y = 3*45 + 22.5 = 157.5
grid_6_3: pixel_x = 6*45 + 22.5 = 292.5, pixel_y = 3*45 + 22.5 = 157.5

distance = √[(247.5 - 292.5)² + (157.5 - 157.5)²]
         = √[(-45)² + 0²]
         = √2025
         = 45.0 píxeles
```

**Invariante**: 
- Movimiento horizontal/vertical: distancia = cell_size = 45 píxeles
- Movimiento diagonal: distancia = 45√2 ≈ 63.6 píxeles (pero solo hay movimientos horizontales/verticales en este grid)

### Vecindad en el Grafo

Para cualquier intersección `intersection_id`, el método `get_neighbors()` retorna sus vecinos accesibles:

```python
def get_neighbors(self, intersection_id: str) -> List[Tuple[str, float]]:
    neighbors = []
    
    for (from_id, to_id), road in self.roads.items():
        # Solo consideramos aristas que salen de intersection_id
        if from_id == intersection_id and road.is_passable:
            
            # Validar que la intersección destino sea accesible
            to_intersection = self.intersections[to_id]
            if to_intersection.is_passable:
                
                # Calcular distancia euclidiana
                distance = √[(px1-px2)² + (py1-py2)²]
                neighbors.append((to_id, distance))
    
    return neighbors
```

**Complejidad**:
- Para cada intersección hay O(1) a O(4) aristas salientes
- En promedio: O(2) aristas (grid interior: 4, grid borde: 2, esquinas: 2)
- Complejidad de `get_neighbors()`: **O(grado del nodo)** ≈ O(1) en este grafo

---

## Algoritmo Dijkstra

### Propósito
Encontrar el **camino más corto** entre dos intersecciones en el grafo.

**Entrada**: 
- `start_intersection`: ID de intersección inicial (ej: "grid_10_6")
- `end_intersection`: ID de intersección final (ej: "grid_2_2")

**Salida**:
- Distancia mínima (en píxeles)
- Secuencia de intersecciones del camino

### Implementación: Clase `OptimizationStrategy`

**Archivo**: `src/optimization_strategies.py`

#### Método 1: `_dijkstra_distance(start, end)` → float

Retorna SOLO la distancia mínima (más rápido si solo necesitas la distancia).

```python
def _dijkstra_distance(self, start_intersection: str, end_intersection: str) -> float:
    
    # Paso 1: Inicializar
    distances = {}
    for inter_id in self.road_grid.intersections:
        distances[inter_id] = float('inf')
    distances[start_intersection] = 0
    
    visited = set()
    priority_queue = [(0, start_intersection)]
    
    # Paso 2: Procesar nodos
    while priority_queue:
        current_distance, current_intersection = heapq.heappop(priority_queue)
        
        # Si ya visitamos este nodo, saltar
        if current_intersection in visited:
            continue
        
        # Si llegamos al destino, retornar la distancia
        if current_intersection == end_intersection:
            return current_distance
        
        visited.add(current_intersection)
        
        # Paso 3: Relajar aristas
        for neighbor_id, edge_distance in self.road_grid.get_neighbors(current_intersection):
            if neighbor_id not in visited:
                new_distance = current_distance + edge_distance
                
                # Si encontramos camino más corto, actualizar
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    heapq.heappush(priority_queue, (new_distance, neighbor_id))
    
    # Si no hay camino, retornar infinito
    return distances[end_intersection]
```

#### Método 2: `_dijkstra_path(start, end)` → List[str]

Retorna la **secuencia de intersecciones** del camino más corto.

```python
def _dijkstra_path(self, start_intersection: str, end_intersection: str) -> List[str]:
    
    # Paso 1: Inicializar estructuras
    distances = {}
    previous = {}  # CAMBIO: Track del camino anterior
    
    for inter_id in self.road_grid.intersections:
        distances[inter_id] = float('inf')
        previous[inter_id] = None
    
    distances[start_intersection] = 0
    visited = set()
    priority_queue = [(0, start_intersection)]
    
    # Paso 2: Procesar nodos (idéntico a _dijkstra_distance)
    while priority_queue:
        current_distance, current_intersection = heapq.heappop(priority_queue)
        
        if current_intersection in visited:
            continue
        visited.add(current_intersection)
        
        # Paso 3: Relajar aristas y registrar el camino anterior
        for neighbor_id, edge_distance in self.road_grid.get_neighbors(current_intersection):
            if neighbor_id not in visited:
                new_distance = current_distance + edge_distance
                
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_intersection  # TRACK: Recordar de dónde vinimos
                    heapq.heappush(priority_queue, (new_distance, neighbor_id))
    
    # Paso 4: Reconstruir camino
    path = []
    current = end_intersection
    
    while current is not None:
        path.append(current)
        current = previous[current]
    
    return path[::-1]  # Invertir para orden correcto (inicio → fin)
```

### Ejemplo Práctico Paso a Paso

**Escenario**: Encontrar camino de `grid_10_6` a `grid_2_2`

```
Iteración 1:
- Nodo actual: grid_10_6 (distancia: 0)
- Vecinos accesibles: 
    - grid_9_6 (distancia: 0 + 45 = 45)
    - grid_11_6 (distancia: 0 + 45 = 45)
    - grid_10_5 (distancia: 0 + 45 = 45)
    - grid_10_7 (distancia: 0 + 45 = 45)
- Encolar todos con sus distancias

Iteración 2:
- Nodo actual: grid_9_6 (distancia: 45)  [Pop del heap]
- Vecinos accesibles:
    - grid_8_6 (distancia: 45 + 45 = 90)
    - grid_9_5 (distancia: 45 + 45 = 90)
    - grid_9_7 (distancia: 45 + 45 = 90)
    - (grid_10_6 ya visitado, se salta)
- Encolar todos...

[Se continúa hasta alcanzar grid_2_2]

Iteración N:
- Nodo actual: grid_2_2 (distancia: 360)
- ¡Llegamos! Retornar 360

Reconstrucción del camino:
- previous[grid_2_2] = grid_3_2
- previous[grid_3_2] = grid_4_2
- previous[grid_4_2] = grid_5_2
- ...
- previous[grid_10_6] = None

Camino: [grid_10_6, grid_9_6, grid_8_6, grid_7_6, grid_6_6, grid_5_6, 
         grid_4_6, grid_3_6, grid_2_6, grid_2_5, grid_2_4, grid_2_3, grid_2_2]
```

### Complejidad de Dijkstra

- **Tiempo**: O((V + E) log V) con heap binario
  - En nuestro caso: V ≈ 240, E ≈ 896
  - O((240 + 896) log 240) ≈ O(8 × 1136) ≈ **O(9088)** operaciones
- **Espacio**: O(V) para estructuras de datos
- **En la práctica**: ~0-5ms por cálculo de distancia

---

## Algoritmo TSP - Vecino Más Cercano

### Propósito
Resolver el **Traveling Salesman Problem (TSP)**: encontrar el orden óptimo de visitar todos los domicilios.

**Definición del Problema**:
- Tenemos un conjunto de POIs: {distribution_center, delivery_1, delivery_2, ..., delivery_15}
- Debemos visitar todos los delivery_X exactamente una vez
- Empezamos en distribution_center
- Minimizar la distancia total

**Entrada**:
- `start_poi`: "distribution_center"
- `destination_pois`: ["delivery_1", "delivery_2", ..., "delivery_15"] (15 domicilios)

**Salida**:
- `OptimizedRoute` con secuencia óptima

### Implementación: `NearestNeighborStrategy`

**Archivo**: `src/optimization_strategies.py`

#### Paso 1: Calcular Matriz de Distancias entre POIs

```python
def _calculate_poi_distance_matrix(self, pois: List[str]) -> Dict[Tuple[str, str], float]:
    """
    Crea matriz de distancias mínimas entre cada par de POIs
    
    Entrada: pois = ["distribution_center", "delivery_1", ..., "delivery_15"]
    Salida: {
        ("distribution_center", "delivery_1"): 315.5,
        ("distribution_center", "delivery_2"): 247.3,
        ("delivery_1", "delivery_2"): 156.8,
        ...
    }
    """
    
    matrix = {}
    
    for from_poi in pois:
        for to_poi in pois:
            if from_poi != to_poi:
                # Obtener las intersecciones mapeadas
                from_intersection = self.road_grid.get_poi_intersection(from_poi)
                to_intersection = self.road_grid.get_poi_intersection(to_poi)
                
                if from_intersection and to_intersection:
                    # Usar Dijkstra para encontrar distancia mínima
                    distance = self._dijkstra_distance(
                        from_intersection.intersection_id,
                        to_intersection.intersection_id
                    )
                    matrix[(from_poi, to_poi)] = distance
    
    return matrix
```

**Complejidad**:
- Para 16 POIs: 16 × 15 = 240 pares
- Cada Dijkstra: O(9088) operaciones
- Total: 240 × 9088 ≈ 2.2M operaciones ≈ **50-100ms**

#### Paso 2: Resolver TSP con Heurística Vecino Más Cercano

```python
def _solve_tsp_nearest_neighbor(self, start_poi: str, destination_pois: List[str],
                                distance_matrix: Dict) -> List[str]:
    """
    Algoritmo greedy: siempre visitar el POI no visitado más cercano
    
    NO es óptimo, pero es rápido O(n²) y da buen resultado.
    """
    
    unvisited = set(destination_pois)  # {"delivery_1", "delivery_2", ..., "delivery_15"}
    path = [start_poi]                  # Comenzar en ["distribution_center"]
    current = start_poi                 # Estamos en distribution_center
    
    while unvisited:  # Mientras haya domicilios no visitados
        # Encontrar el POI no visitado más cercano al actual
        nearest = min(
            unvisited,
            key=lambda dest: distance_matrix.get((current, dest), float('inf'))
        )
        
        # Agregar a la ruta
        path.append(nearest)
        
        # Actualizar estado
        unvisited.remove(nearest)
        current = nearest
    
    return path
```

### Ejemplo Práctico Paso a Paso

```
Iniciales:
- current = "distribution_center" (en grid_10_6)
- unvisited = {"delivery_1", "delivery_2", ..., "delivery_15"}
- path = ["distribution_center"]

Iteración 1:
- Encontrar el delivery más cercano a distribution_center:
  * delivery_1: 315.5 px
  * delivery_2: 247.3 px  ← MÍNIMO
  * delivery_3: 580.2 px
  * ...
- nearest = "delivery_2"
- path = ["distribution_center", "delivery_2"]
- current = "delivery_2"
- unvisited = {"delivery_1", "delivery_3", ..., "delivery_15"}

Iteración 2:
- Encontrar el delivery más cercano a delivery_2:
  * delivery_1: 156.8 px
  * delivery_3: 423.1 px
  * delivery_5: 98.2 px  ← MÍNIMO
  * ...
- nearest = "delivery_5"
- path = ["distribution_center", "delivery_2", "delivery_5"]
- current = "delivery_5"
- unvisited = {"delivery_1", "delivery_3", ..., "delivery_15"} - {"delivery_5"}

[Continuar hasta que unvisited esté vacío]

Final:
- path = ["distribution_center", "delivery_2", "delivery_5", "delivery_6", 
          "delivery_8", "delivery_7", "delivery_4", "delivery_9", "delivery_13",
          "delivery_3", "delivery_12", "delivery_1", "delivery_14", "delivery_11",
          "delivery_10", "delivery_15"]

Nota: Este es un ejemplo, el resultado real depende de la distancia_matrix calculada
```

### Calidad del Resultado

- **Complejidad Temporal**: O(n²) donde n = número de POIs = 16
  - Mucho más rápido que la solución óptima O(n!) = O(16!) ≈ 20 billones
- **Calidad Esperada**: 10-30% peor que óptimo (típico para heurística)
- **Garantía**: No hay (puede ser arbitrariamente malo en casos extremos)
- **Uso**: Base para 2-Opt

---

## Algoritmo 2-Opt

### Propósito
**Mejorar localmente** la ruta de TSP intercambiando pares de aristas.

**Idea Core**: 
Si dos aristas "se cruzan" visualmente, se pueden descruzar invirtiendo el segmento entre ellas, reduciendo la distancia total.

```
ANTES (ineficiente):     DESPUÉS (2-Opt):
  A ─────── B              A ─── D
   \       /                \   /
    \     /                  \ /
     \   /                    /\
      \ /                    /  \
       X                    C ── B
      / \
     /   \
    C     D
```

### Implementación: `TwoOptStrategy`

**Archivo**: `src/optimization_strategies.py`

```python
def _two_opt(self, route: List[str], distance_matrix: Dict) -> Tuple[List[str], int]:
    """
    Algoritmo 2-Opt iterativo: intercambiar aristas hasta no encontrar mejora
    """
    
    best_route = route[:]
    improved = True
    iteration = 0
    
    while improved and iteration < self.max_iterations:  # max_iterations = 1000
        improved = False
        iteration += 1
        best_distance = self._calculate_route_distance(best_route, distance_matrix)
        
        # Intentar todos los posibles intercambios 2-Opt
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route)):
                if j - i == 1:
                    continue  # Saltar nodos adyacentes (no cambia nada)
                
                # PASO CLAVE: Invertir el segmento [i:j]
                # Ruta original:     [..., i-1, i, i+1, ..., j-1, j, j+1, ...]
                # Ruta 2-Opt:        [..., i-1, j-1, ..., i+1, i, j, j+1, ...]
                new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                
                new_distance = self._calculate_route_distance(new_route, distance_matrix)
                
                # Si mejora, mantener el cambio
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
                    break  # Reiniciar búsqueda desde el inicio
            
            if improved:
                break
    
    return best_route, iteration
```

### Ejemplo Práctico Paso a Paso

**Ruta inicial** (de Nearest Neighbor):
```
["distribution_center", "delivery_2", "delivery_5", "delivery_6", 
 "delivery_8", "delivery_7", "delivery_4", "delivery_9", "delivery_13"]

Distancia inicial: 2850.5 px
```

**Iteración 1 de 2-Opt**:

```
Probar i=1, j=3:
  Original: [DC, del_2, del_5, del_6, del_8, ...]
  Invertir [i:j] = [del_2, del_5]:
  Nuevo:    [DC, del_5, del_2, del_6, del_8, ...]
  
  Distancia nueva: 2820.3 px
  ✓ Mejora encontrada! (2850.5 - 2820.3 = 30.2 px)
  
  best_route = [DC, del_5, del_2, del_6, del_8, ...]
  best_distance = 2820.3
  improved = True
  Reiniciar búsqueda

Iteración 2 de 2-Opt:

Probar i=1, j=4:
  Actual: [DC, del_5, del_2, del_6, del_8, ...]
  Invertir [i:j] = [del_5, del_2, del_6]:
  Nuevo:  [DC, del_6, del_2, del_5, del_8, ...]
  
  Distancia nueva: 2785.1 px
  ✓ Mejora encontrada! (2820.3 - 2785.1 = 35.2 px)
  
  best_route = [DC, del_6, del_2, del_5, del_8, ...]
  best_distance = 2785.1
  Reiniciar búsqueda

Iteración N:

Probar todos los pares...
No se encuentra mejora en ninguna iteración.

improved = False → Salir del while loop

Final:
- best_route = [DC, del_6, del_2, del_5, del_8, del_7, del_4, del_9, ...]
- best_distance = 3240.0 px (distancia final optimizada)
- iterations = 3 (se realizaron 3 iteraciones de mejora)
```

### Complejidad de 2-Opt

- **Paso Interior** (por iteración): O(n²) donde n = número de POIs = 16
  - 2 bucles anidados: i de 1 a n-2, j de i+1 a n
  - En promedio: 16 × 16 / 2 = 128 comparaciones por iteración
  - Cada comparación: calcular distancia = O(n) = O(16)
  - Por iteración: O(n²) × O(n) = O(n³) = O(4096) operaciones

- **Outer Loop** (número de mejoras): O(m) donde m = número de iteraciones hasta convergencia
  - Típicamente: 3-10 iteraciones
  - Máximo: 1000 iteraciones

- **Complejidad Total**: O(m × n³) = O(10 × 4096) ≈ **O(40K)** operaciones
  - **En la práctica**: ~1-5ms

### Calidad de 2-Opt

- **Optimalidad**: Local (no garantiza solución global óptima)
- **Mejora esperada**: 5-20% de reducción adicional sobre Nearest Neighbor
- **Convergencia**: Siempre converge a un óptimo local
- **Garantía**: Nunca empeora la solución

---

## Iteración de Datos

### Ciclo Completo: Desde Config hasta Routes

#### Fase 1: Cálculo de Ruta Inicial (Nearest Neighbor)

```
1. GridRouteOptimizer.optimize_route(
       start_poi="distribution_center",
       destination_pois=["delivery_1", ..., "delivery_15"],
       strategy="nearest_neighbor"
   )
   ↓
2. NearestNeighborStrategy.optimize()
   ↓
3.1. Calcular matriz de distancias entre POIs:
     
     for from_poi in ["distribution_center", "delivery_1", ..., "delivery_15"]:
         for to_poi in ["distribution_center", "delivery_1", ..., "delivery_15"]:
             if from_poi != to_poi:
                 from_intersection = get_poi_intersection(from_poi)
                 to_intersection = get_poi_intersection(to_poi)
                 distance = Dijkstra(from_intersection, to_intersection)
                 distance_matrix[(from_poi, to_poi)] = distance
     
     Resultado: 16×16 matriz con 240 entradas
   
   ↓
3.2. Resolver TSP con Vecino Más Cercano:
     
     poi_path = []
     current = "distribution_center"
     unvisited = {"delivery_1", ..., "delivery_15"}
     
     while unvisited not empty:
         nearest = argmin(distance_matrix[(current, d)] for d in unvisited)
         poi_path.append(nearest)
         unvisited.remove(nearest)
         current = nearest
     
     Resultado: poi_path = ["distribution_center", "delivery_2", "delivery_5", ...]
   
   ↓
3.3. Construir ruta completa a través del grid:
     
     full_path = []
     for i in range(len(poi_path) - 1):
         from_poi = poi_path[i]
         to_poi = poi_path[i+1]
         
         from_intersection = get_poi_intersection(from_poi)
         to_intersection = get_poi_intersection(to_poi)
         
         segment = Dijkstra_path(from_intersection, to_intersection)
         
         if i == 0:
             full_path.extend(segment)
         else:
             full_path.extend(segment[1:])  # Evitar duplicar nodo de inicio
     
     Resultado: full_path = ["grid_10_6", "grid_9_6", "grid_8_6", ..., "grid_2_2"]
   
   ↓
3.4. Calcular distancia total:
     
     total_distance = 0
     for i in range(len(poi_path) - 1):
         from_poi = poi_path[i]
         to_poi = poi_path[i+1]
         distance = Dijkstra_distance(from_poi, to_poi)
         total_distance += distance
     
     Resultado: total_distance = 3780.0 px
   
   ↓
4. Retornar OptimizedRoute:
   {
       path: ["distribution_center", "delivery_2", ..., "delivery_15"],
       full_path: ["grid_10_6", "grid_9_6", ..., "grid_2_2"],
       total_distance: 3780.0,
       algorithm_name: "TSP Nearest Neighbor",
       iterations: 0
   }
```

#### Fase 2: Cálculo de Ruta Optimizada (2-Opt)

```
1. GridRouteOptimizer.optimize_route(
       start_poi="distribution_center",
       destination_pois=["delivery_1", ..., "delivery_15"],
       strategy="2opt"
   )
   ↓
2. TwoOptStrategy.optimize()
   ↓
3.1. [Igual a Nearest Neighbor] Calcular matriz de distancias
     ↓
3.2. [Igual a Nearest Neighbor] Resolver TSP inicial
     
     poi_path = ["distribution_center", "delivery_2", "delivery_5", ...]
   
   ↓
3.3. APLICAR 2-OPT:
     
     best_route = poi_path[:]
     improved = True
     iteration = 0
     
     while improved and iteration < 1000:
         improved = False
         iteration += 1
         best_distance = calculate_route_distance(best_route)
         
         for i in range(1, len(best_route) - 2):
             for j in range(i + 1, len(best_route)):
                 if j - i == 1:
                     continue
                 
                 # Invertir segmento [i:j]
                 new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                 new_distance = calculate_route_distance(new_route)
                 
                 if new_distance < best_distance:
                     best_route = new_route
                     best_distance = new_distance
                     improved = True
                     break
             
             if improved:
                 break
     
     Resultado: poi_path = ["distribution_center", "delivery_6", "delivery_2", ...]
                iterations = 3
   
   ↓
3.4. [Igual a Nearest Neighbor] Construir ruta completa a través del grid
     
     full_path = ["grid_10_6", "grid_11_6", "grid_11_5", ..., "grid_2_2"]
   
   ↓
3.5. [Igual a Nearest Neighbor] Calcular distancia total
     
     total_distance = 3240.0 px
   
   ↓
4. Retornar OptimizedRoute:
   {
       path: ["distribution_center", "delivery_6", ..., "delivery_15"],
       full_path: ["grid_10_6", "grid_11_6", ..., "grid_2_2"],
       total_distance: 3240.0,
       algorithm_name: "TSP + 2-Opt Local Search",
       iterations: 3
   }
```

#### Fase 3: Renderizar Comparación

```
1. GridHTMLRenderer.render_comparison(route_nearest, route_optimized)
   ↓
2._generate_html(route_nearest, route_optimized)
   ↓
3. Generar canvas SVG:
   
   for each road in road_grid.roads:
       if is_in_route_nearest or is_in_route_optimized:
           Draw as blue route line (stroke: #3498db)
       elif road.is_passable:
           Draw as gray normal road (stroke: #bbb)
       else:
           Draw as red blocked road (stroke: #ff4444, dashed)
   
   for each intersection in road_grid.intersections:
       if intersection.is_passable:
           if in_route_path_set:
               Draw as active (fill: #e8f4f8, stroke: #3498db)
           else:
               Draw as normal (fill: #f5f7fa, stroke: #999)
   
   for each poi in road_grid.poi_map:
       Draw as circle marker (fill: red para DC, green para delivery)
       Add label con nombre del POI
   
   ↓
4. Generar secciones HTML:
   
   HTML primaria: Ruta nearest
   HTML secundaria: Ruta 2-opt
   
   ↓
5. Escribir output.html con estilos CSS incrustados
```

---

## Generación del Output HTML

### Estructura General del HTML

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ruta de Entrega Optimizada - Grid Avanzado</title>
    <style>
        [CSS inline con todos los estilos]
    </style>
</head>
<body>
    <div class="container">
        <h1>🚚 Ruta de Entrega Optimizada</h1>
        
        <!-- Sección 1: Ruta Nearest Neighbor -->
        <div class="route-section primary-section">
            <h2>📍 Ruta Inicial</h2>
            <div class="info-grid">
                [Cards con información: distancia, intersecciones, algoritmos]
            </div>
            <div class="map-container">
                <svg class="map" viewBox="0 0 900 540">
                    [Canvas: líneas de carreteras, intersecciones, POIs]
                </svg>
            </div>
        </div>
        
        <!-- Sección 2: Ruta 2-Opt Optimizada -->
        <div class="route-section secondary-section">
            <h2>🚀 Ruta Optimizada</h2>
            [Igual estructura que sección 1]
        </div>
        
        <!-- Leyenda -->
        <div class="legend">
            [Explicación de colores y elementos]
        </div>
    </div>
</body>
</html>
```

### Canvas SVG: Elementos Renderizados

**1. Carreteras Normales (grises)**
```svg
<line x1="247.5" y1="157.5" x2="292.5" y2="157.5" class="road"/>
```
- Conecta dos intersecciones
- Color: #bbb (gris claro)
- Grosor: 2px

**2. Carreteras en Ruta (azules)**
```svg
<line x1="450" y1="270" x2="495" y2="270" class="route-road"/>
```
- Carreteras que son parte de la ruta óptima
- Color: #3498db (azul)
- Grosor: 3px
- Opacidad: 0.9

**3. Carreteras Bloqueadas (rojas, punteadas)**
```svg
<line x1="450" y1="45" x2="450" y2="90" class="road-blocked"/>
```
- Carreteras que están bloqueadas (`is_passable=False`)
- Color: #ff4444 (rojo)
- Grosor: 3px
- Patrón: guiones (stroke-dasharray: 4,4)

**4. Intersecciones Normales**
```svg
<circle cx="247.5" cy="157.5" r="3" class="intersection"/>
```
- Punto en el grid que NO es parte de la ruta
- Color: #f5f7fa (muy claro)
- Borde: #999 (gris)

**5. Intersecciones en Ruta**
```svg
<circle cx="450" cy="270" r="3" class="intersection-active"/>
```
- Punto que SÍ es parte de la ruta
- Color: #e8f4f8 (azul muy claro)
- Borde: #3498db (azul)

**6. POIs (Marcadores)**
```svg
<circle cx="450" cy="270" r="8" class="poi-marker"/>
<text x="450" y="288" class="poi-label">Centro Distribución</text>
```
- Centro de distribución: rojo (#e74c3c)
- Domicilios: verde (#27ae60)
- Radio: 8px

### CSS: Estilos Clave

```css
/* Animación de ruta */
@keyframes pulse {
    0%, 100% { stroke-width: 3; opacity: 0.8; }
    50% { stroke-width: 4; opacity: 1; }
}

.route-highlight {
    animation: pulse 2s infinite;
    stroke-linecap: round;
    stroke-linejoin: round;
}

/* Grid responsivo de información */
.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 15px;
}

/* Comparación visual entre rutas */
.primary-section {
    background: #f0f4f8;
    border-left: 5px solid #3498db;
}

.secondary-section {
    background: #f0f8f4;
    border-left: 5px solid #27ae60;
}

.comparison-divider {
    background: linear-gradient(90deg, #667eea, #764ba2);
    height: 3px;
    margin: 30px 0;
}
```

### Ejemplo de Output (Pseudocódigo)

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Ruta de Entrega Optimizada - Grid Avanzado</title>
    <style>
        [800+ líneas de CSS]
    </style>
</head>
<body>
    <div class="container">
        <h1>🚚 Ruta de Entrega Optimizada</h1>
        
        <div class="route-section primary-section">
            <h2>📍 Ruta Inicial</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h3>📊 Estadísticas</h3>
                    <p><strong>Algoritmo:</strong> TSP Nearest Neighbor</p>
                    <p><strong>Distancia Total:</strong> 3780.00 px</p>
                    <p><strong>Intersecciones:</strong> 85</p>
                </div>
            </div>
            <div class="map-container">
                <svg class="map" viewBox="0 0 900 540">
                    <!-- Carreteras grises -->
                    <line x1="22.5" y1="67.5" x2="67.5" y2="67.5" class="road"/>
                    <line x1="67.5" y1="67.5" x2="112.5" y2="67.5" class="road"/>
                    ...
                    
                    <!-- Carreteras bloqueadas (rojas punteadas) -->
                    <line x1="450" y1="45" x2="450" y2="90" class="road-blocked"/>
                    ...
                    
                    <!-- Carreteras en ruta (azules) -->
                    <line x1="450" y1="270" x2="495" y2="270" class="route-road"/>
                    ...
                    
                    <!-- Intersecciones -->
                    <circle cx="247.5" cy="157.5" r="3" class="intersection"/>
                    ...
                    
                    <!-- Intersecciones en ruta -->
                    <circle cx="450" cy="270" r="3" class="intersection-active"/>
                    ...
                    
                    <!-- POIs -->
                    <circle cx="450" cy="270" r="8" class="poi-marker"/>
                    <text x="450" y="288" class="poi-label">Centro Distribución</text>
                    <circle cx="90" cy="90" r="8" class="poi-marker delivery"/>
                    <text x="90" y="108" class="poi-label">Dom. 1</text>
                    ...
                </svg>
            </div>
        </div>
        
        <!-- Sección optimizada similar -->
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #ddd;"></div>
                <span>Carreteras disponibles</span>
            </div>
            ...
        </div>
    </div>
</body>
</html>
```

### Conversión de Grafo a Visualización

```
Grafo (estructura de datos) → SVG (visualización)

grid_5_3 (intersección)
├── pixel_x = 5 * 45 + 22.5 = 247.5
├── pixel_y = 3 * 45 + 22.5 = 157.5
└── is_passable = True
    ↓
    <circle cx="247.5" cy="157.5" r="3" class="intersection"/>

(grid_5_3, grid_6_3) (carretera)
├── from: grid_5_3 (247.5, 157.5)
├── to: grid_6_3 (292.5, 157.5)
├── is_passable = True
└── En ruta = False
    ↓
    <line x1="247.5" y1="157.5" x2="292.5" y2="157.5" class="road"/>

(grid_10_1, grid_10_2) (carretera bloqueada)
├── from: grid_10_1 (450, 45)
├── to: grid_10_2 (450, 90)
├── is_passable = False
└── Dashed = True
    ↓
    <line x1="450" y1="45" x2="450" y2="90" class="road-blocked"/>
```

---

## Resumen de Flujo Completo

```
config.json
    ↓ [Config class: lectura y validación]
├── Grid: width=20, height=12, cell_size=45
├── Nodes: 16 POIs (1 centro, 15 domicilios)
├── blocked_roads: carreteras a bloquear
└── delivery_addresses: domicilios a visitar
    ↓
RoadGrid
    ├── _create_grid():
    │   ├── 240 GridIntersections (20×12)
    │   └── 896 GridRoads (bidireccionales)
    │
    ├── add_poi() × 16:
    │   └── poi_map: {"distribution_center": "grid_10_6", ...}
    │
    └── block_road() × N:
        └── Marcar is_passable=False en carreteras e intersecciones
    
    ↓
Fase 1: NearestNeighborStrategy
    ├── _calculate_poi_distance_matrix():
    │   └── Dijkstra × 240 pares → 16×16 matriz
    │
    ├── _solve_tsp_nearest_neighbor():
    │   └── Greedy loop: elegir vecino más cercano
    │
    ├── _build_full_path():
    │   └── Dijkstra_path × 15 pares → full_path (85 intersecciones)
    │
    └── Resultado: OptimizedRoute (3780 px, 85 intersecciones, 0 iteraciones)
    
    ↓
Fase 2: TwoOptStrategy
    ├── [Pasos 1-3 igual a Nearest Neighbor]
    ├── _two_opt():
    │   ├── Iteración 1: Invertir segmentos → mejora 30.2px
    │   ├── Iteración 2: Invertir segmentos → mejora 35.2px
    │   ├── Iteración 3: Invertir segmentos → mejora 12.1px
    │   └── Convergencia: No más mejoras detectadas
    │
    └── Resultado: OptimizedRoute (3240 px, 73 intersecciones, 3 iteraciones)
    
    ↓
GridHTMLRenderer
    ├── _generate_html():
    │   ├── _generate_css(): 800+ líneas de estilos
    │   └── _generate_primary_section() + _generate_secondary_section()
    │
    ├── _generate_canvas() × 2:
    │   ├── Dibujar 896 carreteras (grises o azules o rojas)
    │   ├── Dibujar 240 intersecciones (blancas o azules)
    │   └── Dibujar 16 POIs (rojo y verde) con etiquetas
    │
    └── output.html
        ├── Sección 1: Ruta Nearest Neighbor
        ├── Sección 2: Ruta 2-Opt optimizada
        ├── Comparación visual lado a lado
        └── Leyenda de colores
```

---

## Notas Técnicas Adicionales

### Modelos de Datos Usados

**Dataclasses** (Python 3.7+):
- `GridIntersection`: Inmutable en lo esencial, mutable `is_passable`
- `GridRoad`: Inmutable en lo esencial, mutable `is_passable`
- `OptimizedRoute`: Immutable (solo lectura)

**Enumeración**:
- `Direction`: Direcciones del grid (no se usa actualmente en código, pero está disponible)

**Tipos Genéricos**:
- `Dict[str, int]`: Configuración
- `List[str]`: Rutas
- `Dict[str, GridIntersection]`: Intersecciones del grafo
- `Dict[Tuple[str, str], GridRoad]`: Aristas del grafo
- `Dict[Tuple[str, str], float]`: Matriz de distancias

### Librerías Utilizadas

```python
import json                           # Lectura de config
import heapq                          # Priority queue para Dijkstra
from typing import Dict, List, Tuple # Type hints
from dataclasses import dataclass    # Definición de estructuras
from enum import Enum                # Enumeraciones
from abc import ABC, abstractmethod   # Herencia abstracta
```

### Complejidades de Memoria

- **RoadGrid**:
  - Intersecciones: 240 × (5 integers + 2 floats) ≈ 7KB
  - Carreteras: 896 × (2 references + 1 boolean) ≈ 9KB
  - POI map: 16 × strings ≈ 1KB
  - **Total**: ~20KB

- **Dijkstra** (por cálculo):
  - distances: 240 × float ≈ 2KB
  - visited: 240 × boolean ≈ 240 bytes
  - priority_queue: O(log 240) items ≈ 1KB
  - **Total**: ~3.2KB

- **Matriz de distancias**:
  - 240 pares × float ≈ 2KB
  - **Total**: ~2KB

- **Output HTML**:
  - SVG con 240 + 896 + 16 elementos ≈ 150-200KB
  - CSS + JS ≈ 50-100KB
  - **Total**: ~250-300KB

### Optimizaciones Futuras

1. **Algoritmos avanzados**:
   - Simulated Annealing
   - Algoritmo Genético (población, crossover, mutación)
   - Lin-Kernighan (5-20% mejor que 2-Opt)

2. **Heurísticas de preprocesamiento**:
   - Remover nodos cercanos (clustering)
   - Dividir problema en subproblemas

3. **Paralelización**:
   - Dijkstra para cada POI en paralelo
   - 2-Opt con threads múltiples

4. **Caché**:
   - Almacenar matrix de distancias en disco
   - Reutilizar cálculos entre ejecuciones

---

## Conclusión

Este sistema implementa un **resolver de TSP práctico** combinando:

1. **Grafo de grid**: Representación de la red vial
2. **Dijkstra**: Camino más corto entre intersecciones
3. **Vecino Más Cercano**: Heurística rápida para TSP
4. **2-Opt**: Mejora local de soluciones

**Resultado final**: Una ruta de entrega que es ~14% más corta que la heurística inicial, generada en ~100-150ms, visualizada en HTML interactivo.
