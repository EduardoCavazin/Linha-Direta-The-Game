import pygame
from src.model.objects.movableObject import MovableObject

class Entity(MovableObject):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, image, status):
        super().__init__(id, position, size, speed)
        self.name = name
        self.health = health
        self.weapon = weapon
        self.ammo = ammo
        self.image = image
        self.status = status

    def move(self, direction, obstacles=None):
        new_position = self.position.copy()

        if direction == "up":
            new_position.y -= self.speed 
        elif direction == "down":
            new_position.y += self.speed
        elif direction == "left":
            new_position.x -= self.speed
        elif direction == "right":
            new_position.x += self.speed

        if obstacles:
            new_hitbox = pygame.Rect(new_position.x, new_position.y, self.size[0], self.size[1])
            for obstacle in obstacles:
                if new_hitbox.colliderect(obstacle.hitbox):
                    return  

        self.position = new_position
        self.hitbox.topleft = (self.position.x, self.position.y)

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
        screen.blit(self.image, self.position)
