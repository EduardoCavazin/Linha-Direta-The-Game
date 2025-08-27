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