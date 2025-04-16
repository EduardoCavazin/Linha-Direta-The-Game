import pygame
from typing import Tuple
from src.model.objects.movableObject import MovableObject

class Bullet(MovableObject):
    def __init__(self, id: str, position: Tuple[float, float], size: Tuple[int, int],
                 speed: float, damage: int, rotation: float) -> None:
        super().__init__(id, position, size, speed, rotation)
        self.damage: int = damage
        self.update_velocity()

    def update(self, delta_time: float, screen_width: int = 800, screen_height: int = 600) -> bool:
        self.position += self.directedSpeed * delta_time
        self.hitbox.topleft = (self.position.x, self.position.y)
        if (self.position.x < 0 or self.position.x > screen_width or
            self.position.y < 0 or self.position.y > screen_height):
            return False
        return True

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox)
