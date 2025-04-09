import pygame
from src.model.objects.movableObject import MovableObject
from src.model.objects.bullet import Bullet
import math

class Entity(MovableObject):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, image, status, rotation=0):
        super().__init__(id, position, size, speed, rotation)
        self.name = name
        self.health = health
        self.weapon = weapon
        self.ammo = ammo
        self.image = image
        self.status = status

    def attack(self, target):
        if self.weapon and self.ammo > 0:
            self.ammo -= 1
            target.take_damage(self.weapon.damage)

    def shoot(self):
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

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        self.status = "dead"
        print(f"Entity {self.id} has died.")

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.position.x, self.position.y))
        else:
            super().draw(screen)
