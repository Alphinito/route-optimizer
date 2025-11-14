from typing import List

class HTMLRenderer:
    """Genera HTML con CSS para visualizar rutas en el mapa"""
    
    def __init__(self, graph, config):
        self.graph = graph
        self.config = config
    
    def render_route(self, route, output_file: str = "output.html"):
        """Renderiza la ruta en un archivo HTML"""
        html_content = self._generate_html(route)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html(self, route) -> str:
        """Genera contenido HTML completo"""
        css = self._generate_css(route)
        canvas = self._generate_canvas(route)
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ruta de Entrega Optimizada</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚚 Ruta de Entrega Optimizada</h1>
        <div class="info-panel">
            <p><strong>Distancia Total:</strong> {route.total_distance:.2f} km</p>
            <p><strong>Domicilios:</strong> {len(route.path) - 1}</p>
            <p><strong>Ruta:</strong> {' → '.join(route.path)}</p>
        </div>
        <svg class="map" viewBox="0 0 1000 800">
            {canvas}
        </svg>
    </div>
</body>
</html>"""
        return html
    
    def _generate_css(self, route) -> str:
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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 30px;
            max-width: 1200px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .info-panel {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        
        .info-panel p {
            margin: 8px 0;
            color: #555;
            font-size: 14px;
        }
        
        .map {
            width: 100%;
            height: 600px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background: #f5f7fa;
        }
        
        .road-blocked {
            stroke: #ddd;
            stroke-dasharray: 5,5;
        }
        
        .node-label {
            font-size: 12px;
            fill: #333;
            text-anchor: middle;
        }
        
        .node-circle {
            stroke: #333;
            stroke-width: 2;
        }
        
        .center-node {
            fill: #e74c3c;
        }
        
        .delivery-node {
            fill: #27ae60;
        }
        
        .route-highlight {
            stroke: #3498db;
            stroke-width: 3;
            fill: none;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { stroke-width: 3; opacity: 1; }
            50% { stroke-width: 4; opacity: 0.8; }
        }"""
    
    def _generate_canvas(self, route) -> str:
        """Genera elementos SVG del mapa"""
        elements = []
        
        # Dibujar todas las carreteras (aristas)
        for edge in self.graph.edges.values():
            from_node = self.graph.nodes[edge.from_node]
            to_node = self.graph.nodes[edge.to_node]
            
            # Evitar duplicados en grafo no dirigido
            if (edge.to_node, edge.from_node) in self.graph.edges:
                if edge.from_node > edge.to_node:
                    continue
            
            is_in_route = edge in route.edges
            class_attr = "route-highlight" if is_in_route else ""
            if edge.is_blocked:
                class_attr += " road-blocked"
            
            line = f'''            <line x1="{from_node.x}" y1="{from_node.y}" 
                   x2="{to_node.x}" y2="{to_node.y}" 
                   class="road {class_attr}" stroke="#999" stroke-width="2"/>'''
            elements.append(line)
        
        # Dibujar todos los nodos
        for node in self.graph.nodes.values():
            node_class = "center-node" if node.node_type == "distribution_center" else "delivery-node"
            
            circle = f'''            <circle cx="{node.x}" cy="{node.y}" r="12" 
                    class="node-circle {node_class}"/>
            <text x="{node.x}" y="{node.y + 25}" class="node-label">{node.name}</text>'''
            elements.append(circle)
        
        return "\n".join(elements)
