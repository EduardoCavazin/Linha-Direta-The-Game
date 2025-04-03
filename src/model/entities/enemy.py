import math
import pygame
from src.model.entities.entity import Entity

class Enemy(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        self.base_enemy_image = pygame.image.load("assets/sprites/player.png")  # ---- MUDAR QUANDO TIVER SPRITE PRO INIMIGO ----
        self.base_enemy_image = pygame.transform.scale(self.base_enemy_image, size)
        self.base_enemy_rect = self.base_enemy_image.get_rect(center=position)

        self.image = self.base_enemy_image
        self.rect = self.image.get_rect(center=self.base_enemy_rect.center)

        self.direction = pygame.Vector2(0, 1)

        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)

    def update_rotation(self, player_position):
        """
        Atualiza a rotação do inimigo para olhar na direção do jogador usando Vector2.
        """
        direction = pygame.Vector2(player_position.x - self.position.x, player_position.y - self.position.y).normalize()
        self.direction = direction
        self.rotation = -math.degrees(math.atan2(direction.y, direction.x))

        self.image = pygame.transform.rotate(self.base_enemy_image, self.rotation)
        self.rect = self.image.get_rect(center=self.base_enemy_rect.center)

    def update(self, player_position):
        """
        Atualiza o estado do inimigo, incluindo sua rotação.
        """
        self.update_rotation(player_position)

    def draw(self, screen):
        """
        Desenha o inimigo na tela.
        """
        screen.blit(self.image, self.rect.topleft)
