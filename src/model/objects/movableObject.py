import pygame
import math
from typing import Tuple, List, Optional
from src.model.objects.gameObject import GameObject

class MovableObject(GameObject):
    def __init__(self, id: str, position: Tuple[float, float], size: Tuple[int, int],
                 speed: float, rotation: float = 0) -> None:
        super().__init__(id, position, size)
        self._position: pygame.Vector2 = pygame.Vector2(position)
        self.speed: float = speed
        self.rotation: float = rotation
        self.directedSpeed: pygame.Vector2 = pygame.Vector2(0, 1)
        self.update_velocity()

    @property
    def position(self) -> pygame.Vector2:
        return self._position

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position = pygame.Vector2(value)
        if hasattr(self, 'hitbox'):
            self.hitbox.topleft = (self._position.x, self._position.y)

    def update_velocity(self) -> None:
        self.directedSpeed = pygame.Vector2(
            math.cos(math.radians(self.rotation)) * self.speed,
            math.sin(math.radians(self.rotation)) * self.speed
        )

    def move(self, direction: str, delta_time: float,
             obstacles: Optional[List[GameObject]] = None,
             screen_width: int = 800, screen_height: int = 600) -> None:
        distance: float = self.speed * delta_time
        new_position: pygame.Vector2 = self.position.copy()

        if direction == "up":
            new_position.y -= distance
        elif direction == "down":
            new_position.y += distance
        elif direction == "left":
            new_position.x -= distance
        elif direction == "right":
            new_position.x += distance

        new_position.x = max(0, min(new_position.x, screen_width - self.size[0]))
        new_position.y = max(0, min(new_position.y, screen_height - self.size[1]))

        if obstacles:
            new_hitbox = pygame.Rect(new_position.x, new_position.y, self.size[0], self.size[1])
            for obstacle in obstacles:
                if new_hitbox.colliderect(obstacle.hitbox):
                    return

        self.position = new_position

    def update(self, direction: str, delta_time: float,
               obstacles: Optional[List[GameObject]] = None,
               screen_width: int = 800, screen_height: int = 600) -> None:
        self.move(direction, delta_time, obstacles, screen_width, screen_height)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (255, 255, 255), self.hitbox)
