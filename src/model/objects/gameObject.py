import pygame

class GameObject:
    def __init__(self, id, position, size):
        self.id = id
        self.position = pygame.Vector2(position)
        self.size = size
        self.hitbox = pygame.Rect(position[0], position[1], size[0], size[1])