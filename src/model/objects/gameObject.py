import pygame
from typing import Tuple

class GameObject:
    def __init__(self, id: str, position: Tuple[float, float], size: Tuple[int, int], hitbox_size: Tuple[int, int] = None) -> None:
        self.id: str = id
        self._position: pygame.Vector2 = pygame.Vector2(position)
        self.size: Tuple[int, int] = size
        
        # Use hitbox_size if provided, otherwise use size
        hitbox_dimensions = hitbox_size if hitbox_size else size
        self.hitbox: pygame.Rect = pygame.Rect(
            position[0] - hitbox_dimensions[0] // 2, 
            position[1] - hitbox_dimensions[1] // 2,
            hitbox_dimensions[0], 
            hitbox_dimensions[1]
        )
