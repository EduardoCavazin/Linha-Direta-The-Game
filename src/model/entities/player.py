import math
import pygame
from typing import Tuple, Optional, Any, List
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
        
       
        self.spritesheet: pygame.Surface = pygame.image.load('assets/sprites/Player_Movement.png')
        self.frame_count: int = 3  
        self.frame_width: int = self.spritesheet.get_width() // self.frame_count
        self.frame_height: int = self.spritesheet.get_height() // 2  
        
        self.frames: List[pygame.Surface] = []
        for y in range(2):  
            for x in range(self.frame_count):
                frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                frame.blit(self.spritesheet, (0, 0), 
                          (x * self.frame_width, y * self.frame_height, 
                           self.frame_width, self.frame_height))
                frame = pygame.transform.scale(frame, size)
                self.frames.append(frame)
        
        self.current_frame: int = 0
        self.animation_speed: float = 0.2  
        self.animation_timer: float = 0
        
        self.base_player_image: pygame.Surface = self.frames[0]
        self.base_player_rect: pygame.Rect = self.base_player_image.get_rect(topleft=topleft)
        
        self.image: pygame.Surface = self.base_player_image
        self.rect: pygame.Rect = self.image.get_rect(topleft=topleft)
        self.direction: pygame.Vector2 = pygame.Vector2(0, 1)
        self.moving: bool = False
        
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
    
    def update_animation(self, delta_time: float) -> None:
        if not self.moving:
            self.current_frame = 0
            self.base_player_image = self.frames[0]
            return
            
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.base_player_image = self.frames[self.current_frame]
    
    def move(
        self,
        direction: str,
        delta_time: float,
        obstacles: Optional[list] = None,
        screen_width: int = 800,
        screen_height: int = 600
    ) -> None:
        self.moving = True 
        super().move(direction, delta_time, obstacles, screen_width, screen_height)
        self.base_player_rect.topleft = (self.position.x, self.position.y)
    
    def reload(self) -> None:
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def calculate_rotation(self) -> float:
        mouse_coords: Tuple[int, int] = pygame.mouse.get_pos()
        player_center: Tuple[float, float] = (self.position.x + self.size[0] / 2,
                                               self.position.y + self.size[1] / 2)
        dx: float = mouse_coords[0] - player_center[0]
        dy: float = mouse_coords[1] - player_center[1]
        if dx == 0 and dy == 0:
            self.direction = pygame.Vector2(0, 1)
            return 0.0
        self.direction = pygame.Vector2(dx, dy).normalize()
    

    def update_sprite(self, angle: float) -> None:
        rotated_image: pygame.Surface = pygame.transform.rotate(self.base_player_image, angle)
        player_center: Tuple[float, float] = (self.position.x + self.size[0] / 2,
                                               self.position.y + self.size[1] / 2)
        self.image = rotated_image
        self.rect = rotated_image.get_rect(center=player_center)

    def draw(self, screen: pygame.Surface) -> None:
        angle: float = -math.degrees(math.atan2(self.direction.y, self.direction.x)) - 90
        self.update_sprite(angle)
        screen.blit(self.image, self.rect.topleft)
        self.moving = False  
