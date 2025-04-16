import pygame
from typing import Tuple

class GameObject:
    def __init__(self, id: str, position: Tuple[float, float], size: Tuple[int, int]) -> None:
        self.id: str = id
        self._position: pygame.Vector2 = pygame.Vector2(position)
        self.size: Tuple[int, int] = size
        self.hitbox: pygame.Rect = pygame.Rect(position[0], position[1], size[0], size[1])
