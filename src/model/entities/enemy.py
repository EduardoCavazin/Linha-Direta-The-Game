import math
import pygame
from typing import Tuple, Optional, Any
from src.model.entities.entity import Entity

class Enemy(Entity):
    def __init__(
        self,
        id: str,
        name: str,
        position: Tuple[float, float],
        size: Tuple[int, int],
        speed: float,
        health: int,
        weapon: Optional[Any],
        ammo: int,
        status: str
    ) -> None:
        self.base_enemy_image: pygame.Surface = pygame.image.load("assets/sprites/player.png")
        self.base_enemy_image = pygame.transform.scale(self.base_enemy_image, size)
        self.base_enemy_rect: pygame.Rect = self.base_enemy_image.get_rect(topleft=position)
        
        self.image: pygame.Surface = self.base_enemy_image
        self.rect: pygame.Rect = self.image.get_rect(topleft=position)
        self.direction: pygame.Vector2 = pygame.Vector2(0, 1)
        
        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)
    
    @property
    def position(self) -> pygame.Vector2:
        return self._position
    
    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position = pygame.Vector2(value)
    
    def update_rotation(self, player_position: pygame.Vector2) -> None:
        direction: pygame.Vector2 = pygame.Vector2(
            player_position.x - self.position.x,
            player_position.y - self.position.y
        )
        if direction.length() != 0:
            direction = direction.normalize()
        self.direction = direction
        self.rotation = -math.degrees(math.atan2(direction.y, direction.x))
        
        self.image = pygame.transform.rotate(self.base_enemy_image, self.rotation)
        self.rect = self.image.get_rect(topleft=self.position)
    
    def update(self, player_position: pygame.Vector2) -> None:
        self.update_rotation(player_position)
    
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)
