import pygame
from src.model.entities.entity import Entity

class Enemy(Entity):
    def __init__(self, id, position, size, speed, health, name, weapon, ammo, status):
        super().__init__(id, position, size, speed, health, name, weapon, ammo, image, status)
        image = pygame.image.load('assets\sprites\enemy.png') 
        image = pygame.transform.scale(image, size)
