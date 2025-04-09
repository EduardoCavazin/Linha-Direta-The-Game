import pygame
import math
from src.model.objects.gameObject import GameObject

class MovableObject(GameObject):
    def __init__(self, id, position, size, speed, rotation=0):
        super().__init__(id, position, size)
        self._position = pygame.Vector2(position)
        self.speed = speed
        self.rotation = rotation
        self.directedSpeed = pygame.Vector2(0, 1)

    def update_velocity(self):
        self.directedSpeed = pygame.Vector2(
            math.cos(math.radians(self.rotation)) * self.speed,
            math.sin(math.radians(self.rotation)) * self.speed
        )

    def move(self, direction, delta_time, obstacles=None, screen_width=800, screen_height=600):
        distance = self.speed * delta_time
        new_position = self.position.copy()

        if direction == "up":
            new_position.y -= distance
        elif direction == "down":
            new_position.y += distance
        elif direction == "left":
            new_position.x -= distance
        elif direction == "right":
            new_position.x += distance

        new_position.x = max(0, min(new_position.x, screen_width - self.size[0]))
        new_position.y = max(0, min(new_position.y, screen_height - self.size[1]))

        if obstacles:
            new_hitbox = pygame.Rect(new_position.x, new_position.y, self.size[0], self.size[1])
            for obstacle in obstacles:
                if new_hitbox.colliderect(obstacle.hitbox):
                    return 

        self.position = new_position

    def update(self, direction, delta_time, obstacles=None, screen_width=800, screen_height=600):
        self.move(direction, delta_time, obstacles, screen_width, screen_height)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.hitbox)
