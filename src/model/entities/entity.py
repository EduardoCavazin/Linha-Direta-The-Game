import pygame
import math
from typing import Tuple, Optional, Any
from src.model.objects.bullet import Bullet
from src.model.objects.movableObject import MovableObject
from src.core.enums import EntityStatus

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
        rotation: float = 0
    ) -> None:
        super().__init__(id, position, size, speed, rotation)
        self.name: str = name
        self.health: int = health
        self.max_health: int = health  
        self.weapon: Optional[Any] = weapon
        self.ammo: int = ammo
        self.image: Optional[pygame.Surface] = image
        self.status: str = status
        
        self._position: pygame.Vector2 = pygame.Vector2(position)
        if image:
            self.rect: pygame.Rect = image.get_rect(center=position)
        else:
            self.rect: pygame.Rect = pygame.Rect(position[0], position[1], size[0], size[1])
        
        self.moving: bool = False
        self.direction: pygame.Vector2 = pygame.Vector2(0, 1)

    @property
    def position(self) -> Tuple[float, float]:
        """Getter da posição da entidade"""
        return (self._position.x, self._position.y)

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        """Setter da posição da entidade"""
        self._position = pygame.Vector2(value)
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
                target_x, target_y = target_pos
                direction = pygame.Vector2(
                    target_x - bullet_pos.x,
                    target_y - bullet_pos.y
                ).normalize()
            else:
                mouse_coords = pygame.mouse.get_pos()
                direction = pygame.Vector2(
                    mouse_coords[0] - bullet_pos.x,
                    mouse_coords[1] - bullet_pos.y
                ).normalize()
            
            rotation = -math.degrees(math.atan2(direction.y, direction.x))
            
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
        player_x, player_y = self._position.x, self._position.y
        target_x, target_y = target_pos
        
        angle_rad = math.atan2(target_y - player_y, target_x - player_x)
        angle_deg = math.degrees(angle_rad)
        
        self.rotation = angle_deg - 90
        
        self.direction = pygame.Vector2(
            math.cos(math.radians(self.rotation + 90)),
            math.sin(math.radians(self.rotation + 90))
        )

    def update_visual(self) -> None:
        if hasattr(self, 'base_image') and self.base_image:
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.base_image, -self.rotation)
            self.rect = self.image.get_rect(center=old_center)
            
    def set_moving(self, is_moving: bool) -> None:
        self.moving = is_moving
        
    def get_distance_to(self, target_pos: Tuple[float, float]) -> float:
        target_x, target_y = target_pos
        return math.sqrt(
            (target_x - self._position.x) ** 2 + 
            (target_y - self._position.y) ** 2
        )
    
    def get_direction_vector(self) -> Tuple[float, float]:
        angle_rad = math.radians(self.rotation)
        return (math.cos(angle_rad), math.sin(angle_rad))
    
    def get_facing_position(self, distance: float = 1.0) -> Tuple[float, float]:
        direction = self.get_direction_vector()
        return (
            self.position[0] + direction[0] * distance,
            self.position[1] + direction[1] * distance
        )
