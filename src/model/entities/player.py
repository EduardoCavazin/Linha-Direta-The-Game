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
        
        self.spritesheet: pygame.Surface = load_image('sprites/Player_Movement.png')
        self.frame_count: int = 3  
        self.frame_width: int = self.spritesheet.get_width() // self.frame_count
        self.frame_height: int = self.spritesheet.get_height() // 2  
        
        self.frames: List[pygame.Surface] = self._load_animation_frames(size)
        
        self.current_frame: int = 0
        self.animation_speed: float = 0.2  
        self.animation_timer: float = 0
        
        self.base_player_image: pygame.Surface = self.frames[0]
        
        self.image: pygame.Surface = self.base_player_image
        self.rect: pygame.Rect = self.image.get_rect(center=position)
        
        self._rect: pygame.Rect = self.rect.copy()
        
        self.direction: pygame.Vector2 = pygame.Vector2(0, 1)
        self.moving: bool = False
        
        self._position: pygame.Vector2 = pygame.Vector2(position)
        
        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)

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
        self.rect.center = (int(self._position.x), int(self._position.y))
        self._rect.center = (int(self._position.x), int(self._position.y))

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
        world_bounds: Optional[Tuple[int, int]] = None
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
            
            if world_bounds:
                self._clamp_to_bounds(world_bounds)

    def _check_collision(self, new_pos: Tuple[float, float], obstacles: Optional[list]) -> bool:
        if not obstacles:
            return False
        
        temp_rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        temp_rect.center = (int(new_pos[0]), int(new_pos[1]))
        
        for obstacle in obstacles:
            if temp_rect.colliderect(obstacle):
                return True
        return False

    def _clamp_to_bounds(self, world_bounds: Tuple[int, int]) -> None:
        half_width = self.size[0] // 2
        half_height = self.size[1] // 2
        
        min_x = half_width
        min_y = half_height
        max_x = world_bounds[0] - half_width
        max_y = world_bounds[1] - half_height
        
        x, y = self.position
        x = max(min_x, min(x, max_x))
        y = max(min_y, min(y, max_y))
        self.position = (x, y)

    def reload(self) -> None:
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def shoot(self, target_world_pos: Optional[Tuple[float, float]] = None) -> Optional['Bullet']:
        if not self.weapon or self.ammo <= 0:
            return None
        
        self.ammo -= 1
        
        from src.model.objects.bullet import Bullet
        
        if target_world_pos is None:
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = mouse_pos
        else:
            mouse_x, mouse_y = target_world_pos
            
        player_x, player_y = self.position
        
        dx = mouse_x - player_x
        dy = mouse_y - player_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            dx, dy = 1, 0
        else:
            dx = dx / distance
            dy = dy / distance
        
        offset = 25 
        bullet_x = player_x + (dx * offset)
        bullet_y = player_y + (dy * offset)
        
        bullet_angle = math.degrees(math.atan2(mouse_y - player_y, mouse_x - player_x))
        
        bullet = Bullet(
            id=f"bullet_{id(self)}_{self.ammo}",
            position=(bullet_x, bullet_y),
            size=(8, 8),
            speed=500,
            damage=self.weapon.damage,
            rotation=bullet_angle
        )
        
        return bullet

    def update(self, delta_time: float) -> None:
        # Remove a rotação automática baseada no mouse aqui
        # A rotação será controlada pelo GameWorld que tem acesso à câmera
        self.update_animation(delta_time)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
        self.moving = False

    def handle_key_press(
        self, 
        key: str, 
        delta_time: float, 
        obstacles: Optional[list] = None,
        world_bounds: Optional[Tuple[int, int]] = None
    ) -> None:
        if key in ["up", "down", "left", "right"]:
            self.move(key, delta_time, obstacles, world_bounds)

    def handle_mouse_click(self):
        return self.shoot()
    
    def rotate_to_mouse(self, mouse_pos: Tuple[int, int]) -> None:
        self.rotate_towards(mouse_pos)
        
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.base_player_image, -self.rotation)
        self.rect = self.image.get_rect(center=old_center) 
