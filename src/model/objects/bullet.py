import pygame
from src.model.objects.movableObject import MovableObject

class Bullet(MovableObject):
    def __init__(self, id, position, size, speed, damage, rotation):
        super().__init__(id, position, size, speed, rotation)
        self.damage = damage
        self.update_velocity()

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox)
