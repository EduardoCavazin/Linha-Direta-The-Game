import pygame
import math
from src.model.objects.gameObject import GameObject

class MovableObject(GameObject):
    def __init__(self, id, position, size, speed, rotation):
        super().__init__(id, position, size)
        self.speed = speed
        self.rotation = rotation
        self.directedSpeed = pygame.Vector2(0, 0)

    def update_velocity(self):
        self.directedSpeed = pygame.Vector2(
            math.cos(math.radians(self.rotation)) * self.speed,
            math.sin(math.radians(self.rotation)) * self.speed
        )

    def move(self):
        self.position += self.directedSpeed
        self.hitbox.topleft = (self.position.x, self.position.y)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.hitbox)  # Representação genérica
