import math
import pygame
from typing import Tuple, Union

def calculate_distance(pos1: Union[pygame.Vector2, Tuple[float, float]], 
                      pos2: Union[pygame.Vector2, Tuple[float, float]]) -> float:
    """Calcula a distância euclidiana entre dois pontos"""
    if isinstance(pos1, pygame.Vector2):
        x1, y1 = pos1.x, pos1.y
    else:
        x1, y1 = pos1
        
    if isinstance(pos2, pygame.Vector2):
        x2, y2 = pos2.x, pos2.y
    else:
        x2, y2 = pos2
    
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calculate_angle_to_target(from_pos: Union[pygame.Vector2, Tuple[float, float]], 
                             to_pos: Union[pygame.Vector2, Tuple[float, float]]) -> float:
    """Calcula o ângulo em graus para um alvo"""
    if isinstance(from_pos, pygame.Vector2):
        x1, y1 = from_pos.x, from_pos.y
    else:
        x1, y1 = from_pos
        
    if isinstance(to_pos, pygame.Vector2):
        x2, y2 = to_pos.x, to_pos.y
    else:
        x2, y2 = to_pos
    
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def normalize_direction(dx: float, dy: float) -> Tuple[float, float]:
    """Normaliza um vetor direção"""
    distance = math.sqrt(dx * dx + dy * dy)
    if distance == 0:
        return (0, 0)
    return (dx / distance, dy / distance)

def create_direction_vector(from_pos: Union[pygame.Vector2, Tuple[float, float]], 
                           to_pos: Union[pygame.Vector2, Tuple[float, float]]) -> pygame.Vector2:
    """Cria um vetor direção normalizado entre dois pontos"""
    if isinstance(from_pos, pygame.Vector2):
        x1, y1 = from_pos.x, from_pos.y
    else:
        x1, y1 = from_pos
        
    if isinstance(to_pos, pygame.Vector2):
        x2, y2 = to_pos.x, to_pos.y
    else:
        x2, y2 = to_pos
    
    direction = pygame.Vector2(x2 - x1, y2 - y1)
    if direction.length() > 0:
        return direction.normalize()
    return pygame.Vector2(0, 0)

def create_triangle_vertices(center: Union[pygame.Vector2, Tuple[float, float]], 
                           width: float, 
                           height: float, 
                           rotation: float) -> Tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]:
    """
    Cria os vértices de um triângulo baseado no centro, dimensões e rotação.
    
    Args:
        center: Centro do triângulo
        width: Largura da base (ombros)
        height: Altura do triângulo (centro até ponta)
        rotation: Rotação em graus (0 = ponta para cima)
    
    Returns:
        Tupla com os 3 vértices: (ponta, base_esquerda, base_direita)
    """
    if isinstance(center, pygame.Vector2):
        center_x, center_y = center.x, center.y
    else:
        center_x, center_y = center
    
    # Triângulo local (antes da rotação)
    # Ponta para cima, base para baixo
    local_vertices = [
        pygame.Vector2(0, height/2),               # Ponta (frente)
        pygame.Vector2(-width/2, -height/2),       # Base esquerda (ombro esquerdo)
        pygame.Vector2(width/2, -height/2)         # Base direita (ombro direito)
    ]
    
    # Aplicar rotação
    rotation_rad = math.radians(rotation)
    cos_rot = math.cos(rotation_rad)
    sin_rot = math.sin(rotation_rad)
    
    rotated_vertices = []
    for vertex in local_vertices:
        # Matriz de rotação 2D
        rotated_x = vertex.x * cos_rot - vertex.y * sin_rot
        rotated_y = vertex.x * sin_rot + vertex.y * cos_rot
        
        # Translatar para posição no mundo
        world_vertex = pygame.Vector2(
            rotated_x + center_x,
            rotated_y + center_y
        )
        rotated_vertices.append(world_vertex)
    
    return tuple(rotated_vertices)

def point_in_triangle(point: Union[pygame.Vector2, Tuple[float, float]], 
                     triangle_vertices: Tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]) -> bool:
    """
    Verifica se um ponto está dentro de um triângulo usando coordenadas baricêntricas.
    
    Args:
        point: Ponto a ser testado
        triangle_vertices: Tupla com os 3 vértices do triângulo
    
    Returns:
        True se o ponto está dentro do triângulo
    """
    if isinstance(point, pygame.Vector2):
        point_vec = point
    else:
        point_vec = pygame.Vector2(point)
    
    v0, v1, v2 = triangle_vertices
    
    # Calcular vetores
    v0v1 = v1 - v0
    v0v2 = v2 - v0
    v0p = point_vec - v0
    
    # Calcular produtos escalares
    dot00 = v0v2.dot(v0v2)
    dot01 = v0v2.dot(v0v1)
    dot02 = v0v2.dot(v0p)
    dot11 = v0v1.dot(v0v1)
    dot12 = v0v1.dot(v0p)
    
    # Evitar divisão por zero
    denom = dot00 * dot11 - dot01 * dot01
    if abs(denom) < 1e-10:
        return False
    
    # Calcular coordenadas baricêntricas
    inv_denom = 1 / denom
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom
    
    # Verificar se o ponto está dentro do triângulo
    return (u >= 0) and (v >= 0) and (u + v <= 1)

def triangle_rect_collision(triangle_vertices: Tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2], 
                          rect: pygame.Rect) -> bool:
    """
    Verifica colisão entre um triângulo e um retângulo usando SAT (Separating Axis Theorem).
    
    Args:
        triangle_vertices: Tupla com os 3 vértices do triângulo
        rect: Retângulo pygame
    
    Returns:
        True se há colisão
    """
    # Converter rect para vértices
    rect_vertices = [
        pygame.Vector2(rect.left, rect.top),
        pygame.Vector2(rect.right, rect.top),
        pygame.Vector2(rect.right, rect.bottom),
        pygame.Vector2(rect.left, rect.bottom)
    ]
    
    return sat_polygon_collision(list(triangle_vertices), rect_vertices)

def triangle_triangle_collision(triangle1_vertices: Tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2],
                              triangle2_vertices: Tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]) -> bool:
    """
    Verifica colisão entre dois triângulos usando SAT.
    
    Args:
        triangle1_vertices: Vértices do primeiro triângulo
        triangle2_vertices: Vértices do segundo triângulo
    
    Returns:
        True se há colisão
    """
    return sat_polygon_collision(list(triangle1_vertices), list(triangle2_vertices))

def sat_polygon_collision(vertices1: list, vertices2: list) -> bool:
    """
    Separating Axis Theorem para detecção de colisão entre polígonos convexos.
    
    Args:
        vertices1: Lista de vértices do primeiro polígono (pygame.Vector2)
        vertices2: Lista de vértices do segundo polígono (pygame.Vector2)
    
    Returns:
        True se há colisão
    """
    # Obter todos os eixos de separação (normais das arestas)
    axes = []
    
    # Eixos do primeiro polígono
    for i in range(len(vertices1)):
        edge = vertices1[(i + 1) % len(vertices1)] - vertices1[i]
        if edge.length() > 0:  # Evitar vetores zero
            normal = pygame.Vector2(-edge.y, edge.x).normalize()
            axes.append(normal)
    
    # Eixos do segundo polígono
    for i in range(len(vertices2)):
        edge = vertices2[(i + 1) % len(vertices2)] - vertices2[i]
        if edge.length() > 0:  # Evitar vetores zero
            normal = pygame.Vector2(-edge.y, edge.x).normalize()
            axes.append(normal)
    
    # Testar separação em cada eixo
    for axis in axes:
        # Projetar ambos os polígonos no eixo
        proj1 = project_polygon_on_axis(vertices1, axis)
        proj2 = project_polygon_on_axis(vertices2, axis)
        
        # Se há separação neste eixo, não há colisão
        if proj1[1] < proj2[0] or proj2[1] < proj1[0]:
            return False
    
    # Se não há separação em nenhum eixo, há colisão
    return True

def project_polygon_on_axis(vertices: list, axis: pygame.Vector2) -> Tuple[float, float]:
    """
    Projeta um polígono em um eixo e retorna o intervalo (min, max).
    
    Args:
        vertices: Lista de vértices (pygame.Vector2)
        axis: Eixo de projeção normalizado (pygame.Vector2)
    
    Returns:
        Tupla (min_projection, max_projection)
    """
    if not vertices:
        return (0, 0)
    
    dots = [vertex.dot(axis) for vertex in vertices]
    return (min(dots), max(dots))

def triangle_bounding_rect(triangle_vertices: Tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]) -> pygame.Rect:
    """
    Calcula o retângulo que contém todo o triângulo (útil para otimizações).
    
    Args:
        triangle_vertices: Vértices do triângulo
    
    Returns:
        pygame.Rect que contém o triângulo
    """
    min_x = min(v.x for v in triangle_vertices)
    max_x = max(v.x for v in triangle_vertices)
    min_y = min(v.y for v in triangle_vertices)
    max_y = max(v.y for v in triangle_vertices)
    
    return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)