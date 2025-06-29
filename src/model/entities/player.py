import math
import pygame
from typing import Tuple, Optional, Any, List
from src.model.entities.entity import Entity
from src.core.utils import load_image
from src.model.objects.bullet import Bullet


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
        
        self.spritesheet: pygame.Surface = load_image('Player_Movement.png')
        self.frame_count: int = 3  
        self.frame_width: int = self.spritesheet.get_width() // self.frame_count
        self.frame_height: int = self.spritesheet.get_height() // 2  
        
        self.frames: List[pygame.Surface] = self._load_animation_frames(size)
        
        self.current_frame: int = 0
        self.animation_speed: float = 0.2  
        self.animation_timer: float = 0
        
        self.base_player_image: pygame.Surface = self.frames[0]
        self.base_player_rect: pygame.Rect = self.base_player_image.get_rect(topleft=position)
        
        self.image: pygame.Surface = self.base_player_image
        self.rect: pygame.Rect = self.image.get_rect(topleft=position)
        self.direction: pygame.Vector2 = pygame.Vector2(0, 1)
        self.moving: bool = False
        
        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)
        
        self._position: pygame.Vector2 = pygame.Vector2(position)
    
    def _load_animation_frames(self, size: Tuple[int, int]) -> List[pygame.Surface]:
        frames = []
        for y in range(2):
            for x in range(self.frame_count):
                frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                frame.blit(self.spritesheet, (0, 0), 
                          (x * self.frame_width, y * self.frame_height, 
                           self.frame_width, self.frame_height))
                frame = pygame.transform.scale(frame, size)
                frames.append(frame)
        return frames
    
    @property
    def position(self) -> Tuple[float, float]:
        return (self._position.x, self._position.y)
    
    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position = pygame.Vector2(value)
        self._rect.topleft = (int(self._position.x), int(self._position.y))
    
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
        screen_bounds: Optional[Tuple[int, int]] = None
    ) -> None:
        self.moving = True
        
        speed = self.speed * delta_time
        current_pos = self.position
        
        new_pos = current_pos
        if direction == "up":
            new_pos = (current_pos[0], current_pos[1] - speed)
        elif direction == "down":
            new_pos = (current_pos[0], current_pos[1] + speed)
        elif direction == "left":
            new_pos = (current_pos[0] - speed, current_pos[1])
        elif direction == "right":
            new_pos = (current_pos[0] + speed, current_pos[1])
        
        if not self._check_collision(new_pos, obstacles):
            self.position = new_pos
            
            if screen_bounds:
                self._clamp_to_bounds(screen_bounds)

    def _check_collision(self, new_pos: Tuple[float, float], obstacles: Optional[list]) -> bool:
        if not obstacles:
            return False
        
        temp_rect = pygame.Rect(new_pos[0], new_pos[1], self.size[0], self.size[1])
        
        for obstacle in obstacles:
            if temp_rect.colliderect(obstacle):
                return True
        return False

    def _clamp_to_bounds(self, screen_bounds: Tuple[int, int]) -> None:
        max_x = screen_bounds[0] - self.size[0]
        max_y = screen_bounds[1] - self.size[1]
        
        x, y = self.position
        x = max(0, min(x, max_x))
        y = max(0, min(y, max_y))
        self.position = (x, y)

    def reload(self) -> None:
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def shoot(self) -> Optional['Bullet']:
        if not self.weapon or self.ammo <= 0:
            return None
        
        self.ammo -= 1
        
        from src.model.objects.bullet import Bullet
        
        bullet_pos = (
            self.position[0] + self.size[0] / 2,
            self.position[1] + self.size[1] / 2
        )
        
        bullet = Bullet(
            id=f"bullet_{id(self)}_{self.ammo}",
            position=bullet_pos,
            size=(8, 8),
            speed=500,
            damage=self.weapon.damage,
            rotation=self.rotation
        )
        
        return bullet

    def draw(self, screen: pygame.Surface) -> None:
        self.update_animation(0)  
        screen.blit(self.image, self.rect.topleft)
        self.moving = False

    def handle_key_press(
        self, 
        key: str, 
        delta_time: float, 
        obstacles: Optional[list] = None,
        screen_bounds: Optional[Tuple[int, int]] = None
    ) -> None:
        if key in ["up", "down", "left", "right"]:
            self.move(key, delta_time, obstacles, screen_bounds)

    def handle_mouse_click(self):
        return self.shoot()
    
    def rotate_to_mouse(self, mouse_pos: Tuple[int, int]) -> None:
        
        self.rotate_towards(mouse_pos)
        
        self.image = pygame.transform.rotate(self.base_player_image, -self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
