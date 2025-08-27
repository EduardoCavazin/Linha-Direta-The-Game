import pygame
import math
from typing import Tuple, Optional, Any, List, Union
from src.model.objects.bullet import Bullet
from src.model.objects.movableObject import MovableObject
from src.core.enums import EntityStatus
from src.core.utils import load_image, create_surface
from src.core.mathUtils import calculate_distance, calculate_angle_to_target, create_direction_vector
from src.core.constants import Physics

class Entity(MovableObject):
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
        image: Optional[pygame.Surface],
        status: str,
        rotation: float = 0,
        sprite_config: Optional[dict] = None
    ) -> None:
        super().__init__(id, position, size, speed, rotation)
        self.name: str = name
        self.health: int = health
        self.max_health: int = health  
        self.weapon: Optional[Any] = weapon
        self.ammo: int = ammo
        self.image: Optional[pygame.Surface] = image
        self.status: str = status
        
        # Animation setup
        self._setup_animation(sprite_config, image, size)
        
        self._position: pygame.Vector2 = pygame.Vector2(position)
        if image:
            self.rect: pygame.Rect = image.get_rect(center=position)
        else:
            self.rect: pygame.Rect = pygame.Rect(position[0], position[1], size[0], size[1])
        
        self.moving: bool = False
        self.direction: pygame.Vector2 = pygame.Vector2(0, 1)

    def _setup_animation(self, sprite_config: Optional[dict], image: Optional[pygame.Surface], size: Tuple[int, int]) -> None:
        """Configura o sistema de animação da entidade"""
        sprite_config = sprite_config or {}
        
        self.frame_count = sprite_config.get("frames", 1)
        self.frame_rows = sprite_config.get("frame_rows", 1)  # Novo: suporte a linhas
        self.animation_speed = sprite_config.get("animation_speed", 0.2)
        self.current_frame = 0
        self.animation_timer = 0.0
        
        # If it's an animated sprite, load frames
        if self.frame_count > 1 and image:
            self.frames = self._load_animation_frames(image, size)
            self.base_image = self.frames[0] if self.frames else image
        else:
            self.base_image = image
            self.frames = [image] if image else []
    
    def _load_animation_frames(self, spritesheet: pygame.Surface, size: Tuple[int, int]) -> List[pygame.Surface]:
        """Simplified animation frame loader - supports both 1xN and MxN spritesheets"""
        frames = []
        if self.frame_count <= 1:
            return [spritesheet]
        
        # Calculate frame dimensions based on layout
        if self.frame_rows > 1:
            # Multi-row spritesheet (MxN grid)
            frame_width = spritesheet.get_width() // self.frame_count
            frame_height = spritesheet.get_height() // self.frame_rows
            
            # Load row by row, frame by frame
            for y in range(self.frame_rows):
                for x in range(self.frame_count):
                    frame = self._extract_frame(spritesheet, x * frame_width, y * frame_height, 
                                              frame_width, frame_height, size)
                    frames.append(frame)
        else:
            # Single row horizontal spritesheet (1xN)
            frame_width = spritesheet.get_width() // self.frame_count
            frame_height = spritesheet.get_height()
            
            for x in range(self.frame_count):
                frame = self._extract_frame(spritesheet, x * frame_width, 0, 
                                          frame_width, frame_height, size)
                frames.append(frame)
        
        return frames
    
    def _extract_frame(self, spritesheet: pygame.Surface, x: int, y: int, 
                      width: int, height: int, target_size: Tuple[int, int]) -> pygame.Surface:
        """Extract and scale a single frame from spritesheet"""
        frame = create_surface((width, height))
        frame.blit(spritesheet, (0, 0), (x, y, width, height))
        return pygame.transform.scale(frame, target_size)
    
    def update_animation(self, delta_time: float) -> None:
        """Atualiza a animação da entidade"""
        if self.frame_count <= 1 or not self.frames:
            return
            
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % self.frame_count
            if self.current_frame < len(self.frames):
                self.base_image = self.frames[self.current_frame]

    @property
    def position(self) -> pygame.Vector2:
        """Getter da posição da entidade - returns Vector2 for consistency"""
        return self._position

    @position.setter
    def position(self, value: Union[pygame.Vector2, Tuple[float, float]]) -> None:
        """Setter da posição da entidade - accepts Vector2 or tuple"""
        if isinstance(value, tuple):
            self._position = pygame.Vector2(value)
        else:
            self._position = value
        self.rect.center = (int(self._position.x), int(self._position.y))
        self.hitbox.center = (int(self._position.x), int(self._position.y))

    def attack(self, target: 'Entity') -> None:
        if self.weapon and self.ammo > 0:
            self.ammo -= 1
            target.take_damage(self.weapon.damage)

    def shoot(self, target_pos: Optional[Tuple[float, float]] = None) -> Optional[Bullet]:
        """Dispara uma bala se tiver arma e munição"""
        if self.weapon and self.ammo > 0:
            self.ammo -= 1
            
            bullet_pos = pygame.Vector2(self._position.x, self._position.y)
            
            if target_pos:
                direction = create_direction_vector(bullet_pos, target_pos)
                rotation = calculate_angle_to_target(bullet_pos, target_pos)
            else:
                mouse_coords = pygame.mouse.get_pos()
                direction = create_direction_vector(bullet_pos, mouse_coords)
                rotation = calculate_angle_to_target(bullet_pos, mouse_coords)
            
            rotation = -rotation
            
            if hasattr(self.weapon, 'bullet_config'):
                bullet_size = tuple(self.weapon.bullet_config.get('size', [8, 8]))
                bullet_speed = self.weapon.bullet_config.get('speed', 500)
            else:
                bullet_size = (8, 8)
                bullet_speed = 500
            
            bullet = Bullet(
                id=f"bullet_{self.id}",
                position=bullet_pos,
                size=bullet_size,
                speed=bullet_speed,
                damage=self.weapon.damage,
                rotation=rotation
            )
            bullet.directedSpeed = direction * bullet.speed
            return bullet
        else:
            print(f"{self.name} está sem munição!")
            return None


    def take_damage(self, damage: int) -> None:
        if self.is_alive():
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.die()
                
    def heal(self, amount: int) -> None:
        if self.is_alive():
            self.health = min(self.max_health, self.health + amount)

    def die(self) -> None:
        self.status = EntityStatus.DEAD.value
        print(f"{self.name} morreu!")
        
    def is_alive(self) -> bool:
        return self.status != EntityStatus.DEAD.value
        
    def get_health_percentage(self) -> float:
        return (self.health / self.max_health) * 100.0 if self.max_health > 0 else 0.0

    def draw(self, screen: pygame.Surface) -> None:
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            rect = pygame.Rect(self._position.x, self._position.y, self.size[0], self.size[1])
            pygame.draw.rect(screen, (255, 0, 255), rect)

    def rotate_towards(self, target_pos: Tuple[float, float]) -> None:
        current_pos = (self._position.x, self._position.y)
        angle_deg = calculate_angle_to_target(current_pos, target_pos)
        
        self.rotation = angle_deg - Physics.DIRECTION_OFFSET_DEGREES
        
        self.direction = pygame.Vector2(
            math.cos(math.radians(self.rotation + Physics.DIRECTION_OFFSET_DEGREES)),
            math.sin(math.radians(self.rotation + Physics.DIRECTION_OFFSET_DEGREES))
        )

    def update_visual(self) -> None:
        if hasattr(self, 'base_image') and self.base_image:
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.base_image, -self.rotation)
            self.rect = self.image.get_rect(center=old_center)
            
    def set_moving(self, is_moving: bool) -> None:
        self.moving = is_moving
        
    def get_distance_to(self, target_pos: Tuple[float, float]) -> float:
        return calculate_distance(self._position, target_pos)
    
    def get_direction_vector(self) -> Tuple[float, float]:
        angle_rad = math.radians(self.rotation)
        return (math.cos(angle_rad), math.sin(angle_rad))
    
    def get_facing_position(self, distance: float = 1.0) -> Tuple[float, float]:
        direction = self.get_direction_vector()
        return (
            self.position[0] + direction[0] * distance,
            self.position[1] + direction[1] * distance
        )
