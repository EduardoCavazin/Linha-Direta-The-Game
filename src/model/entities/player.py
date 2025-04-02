import pygame
from src.model.entities.entity import Entity

class Player(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        # Carregar e ajustar a imagem primeiro
        image = pygame.image.load('assets/sprites/player.png')
        image = pygame.transform.scale(image, size)
        # Agora, chame o construtor da superclasse com a imagem carregada
        super().__init__(id, name, position, size, speed, health, weapon, ammo, image, status)

    def reload(self):
        if self.weapon:
            self.ammo = self.weapon.max_ammo
