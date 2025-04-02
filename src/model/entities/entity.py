import pygame
from src.model.objects.movableObject import MovableObject

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
