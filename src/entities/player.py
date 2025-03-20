import pygame
from src.entities.entity import Entity

class Player(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        super().__init__(id, position, size, speed, health, status)
        self.name = name
        self.weapon = weapon
        self.ammo = ammo
        self.image = pygame.image.load('assets\sprites\player.png')  # Carregar a imagem do jogador
        self.image = pygame.transform.scale(self.image, size)  # Redimensionar a imagem para o tamanho especificado

    def attack(self, target):
        if self.weapon and self.ammo > 0:
            self.ammo -= 1
            target.take_damage(self.weapon.damage)

    def reload(self):
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def draw(self, screen):
        screen.blit(self.image, self.position)