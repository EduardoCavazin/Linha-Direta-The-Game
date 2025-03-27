import pygame
from src.model.entities.entity import Entity

class Player(Entity):
    def __init__(self, id, position, size, speed, health, name, weapon, ammo, status):
        image = pygame.image.load('assets\sprites\player.png') 
        image = pygame.transform.scale(image, size)
        super().__init__(id, position, size, speed, health, name, weapon, ammo, image, status)

    def reload(self):
        if self.weapon:
            self.ammo = self.weapon.max_ammo