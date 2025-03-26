import pygame
from src.entities.gameObject import GameObject

class Entity(GameObject):
    def __init__(self, id, position, size, speed, health, status):
        super().__init__(id, position, size)
        self.speed = speed
        self.health = health
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

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        self.status = "dead"
        print(f"Entity {self.id} has died.")