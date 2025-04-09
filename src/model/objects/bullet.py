import pygame
from src.model.objects.movableObject import MovableObject

class Bullet(MovableObject):
    def __init__(self, id, position, size, speed, damage, rotation):
        super().__init__(id, position, size, speed, rotation)
        self.damage = damage
        self.update_velocity()

    def update(self, delta_time, screen_width=800, screen_height=600):
        self.position += self.directedSpeed * delta_time

        self.hitbox.topleft = (self.position.x, self.position.y)

        if (self.position.x < 0 or self.position.x > screen_width or
                self.position.y < 0 or self.position.y > screen_height):
            return False  
        return True

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox)
