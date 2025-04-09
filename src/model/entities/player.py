import math
import pygame
from typing import Tuple, Optional, Any
from src.model.entities.entity import Entity

class Player(Entity):
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
        topleft: Tuple[float, float] = (position[0] - size[0] // 2, position[1] - size[1] // 2)
        
        self.base_player_image: pygame.Surface = pygame.image.load('assets/sprites/player.png')
        self.base_player_image = pygame.transform.scale(self.base_player_image, size)
        
        self.base_player_rect: pygame.Rect = self.base_player_image.get_rect(topleft=topleft)
        
        self.image: pygame.Surface = self.base_player_image
        self.rect: pygame.Rect = self.image.get_rect(topleft=topleft)
        
        self.direction: pygame.Vector2 = pygame.Vector2(0, 1)
        
        super().__init__(id, name, topleft, size, speed, health, weapon, ammo, self.image, status)
        
        self._position: pygame.Vector2 = pygame.Vector2(topleft)
    
    @property
    def position(self) -> pygame.Vector2:
        return self._position
    
    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position = pygame.Vector2(value)
        if hasattr(self, 'hitbox'):
            self.hitbox.topleft = (self._position.x, self._position.y)
    
    def move(self, direction: str, delta_time: float, obstacles: Optional[list] = None,
             screen_width: int = 800, screen_height: int = 600) -> None:
        super().move(direction, delta_time, obstacles, screen_width, screen_height)
        self.base_player_rect.topleft = (self.position.x, self.position.y)
    
    def reload(self) -> None:
        if self.weapon:
            self.ammo = self.weapon.max_ammo
    
    def player_turning(self) -> None:
        mouse_coords: Tuple[int, int] = pygame.mouse.get_pos()
        player_center: Tuple[float, float] = (self.position.x + self.size[0] // 2, self.position.y + self.size[1] // 2)
        dx: float = mouse_coords[0] - player_center[0]
        dy: float = mouse_coords[1] - player_center[1]
        self.direction = pygame.Vector2(dx, dy).normalize()
        angle: float = -math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(self.base_player_image, angle)
        self.rect = self.image.get_rect(center=player_center)
    
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)
