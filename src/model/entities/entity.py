import pygame
import math
from typing import Tuple, Optional, Any
from src.model.objects.bullet import Bullet
from src.model.objects.movableObject import MovableObject

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
        self.weapon: Optional[Any] = weapon
        self.ammo: int = ammo
        self.image: Optional[pygame.Surface] = image
        self.status: str = status

    def attack(self, target: 'Entity') -> None:
        if self.weapon and self.ammo > 0:
            self.ammo -= 1
            target.take_damage(self.weapon.damage)

    def shoot(self) -> Optional[Bullet]:
        if self.weapon and self.ammo > 0:
            self.ammo -= 1
            bullet_position = pygame.Vector2(
                self.position.x + self.size[0] // 2,
                self.position.y + self.size[1] // 2
            )
            mouse_coords = pygame.mouse.get_pos()
            direction = pygame.Vector2(
                mouse_coords[0] - bullet_position.x,
                mouse_coords[1] - bullet_position.y
            ).normalize()
            rotation = -math.degrees(math.atan2(direction.y, direction.x))
            bullet = Bullet(
                id=f"bullet_{self.id}",
                position=bullet_position,
                size=(5, 5),
                speed=2000,
                damage=self.weapon.damage,
                rotation=rotation
            )
            bullet.directedSpeed = direction * bullet.speed
            return bullet
        else:
            print(f"{self.name} está sem munição!")
            return None


    def take_damage(self, damage: int) -> None:
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self) -> None:
        self.status = "dead"
        print(f"Entity {self.id} has died.")
        
    def is_alive(self) -> bool:
        return self.status != "dead"

    def draw(self, screen: pygame.Surface) -> None:
        if self.image:
            screen.blit(self.image, (self.position.x, self.position.y))
        else:
            super().draw(screen)

    def rotate_towards(self, target_pos: Tuple[float, float]) -> None:
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        
        angle_rad = math.atan2(dy, dx)
        self.rotation = math.degrees(angle_rad)
    
    def get_direction_vector(self) -> Tuple[float, float]:
        angle_rad = math.radians(self.rotation)
        return (math.cos(angle_rad), math.sin(angle_rad))
    
    def get_facing_position(self, distance: float = 1.0) -> Tuple[float, float]:
        direction = self.get_direction_vector()
        return (
            self.position[0] + direction[0] * distance,
            self.position[1] + direction[1] * distance
        )
