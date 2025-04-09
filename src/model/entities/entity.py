import pygame
from typing import Tuple, Optional, Any
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

    def take_damage(self, damage: int) -> None:
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self) -> None:
        self.status = "dead"
        print(f"Entity {self.id} has died.")

    def draw(self, screen: pygame.Surface) -> None:
        if self.image:
            screen.blit(self.image, (self.position.x, self.position.y))
        else:
            super().draw(screen)
