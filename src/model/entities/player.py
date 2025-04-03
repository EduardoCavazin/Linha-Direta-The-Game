import math
import pygame
from src.model.entities.entity import Entity

class Player(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        self.base_player_image = pygame.image.load('assets/sprites/player.png')
        self.base_player_image = pygame.transform.scale(self.base_player_image, size)
        self.base_player_rect = self.base_player_image.get_rect(center=position)

        self.image = self.base_player_image
        self.rect = self.image.get_rect(center=self.base_player_rect.center)

        self.direction = pygame.Vector2(0, 1) 
        
        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)
    
    def update(self):
        self.player_turning()
    
    def move(self, direction, delta_time, obstacles=None):
        super().move(direction, delta_time, obstacles)
        # Atualiza o centro do retângulo base com a nova posição
        self.base_player_rect.center = (self.position.x, self.position.y)
    
    def reload(self):
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def player_turning(self):
        """
        Atualiza a direção do jogador com base na posição do mouse em relação à posição do jogador.
        """
        # Pega as coordenadas do mouse em pixels
        self.mouse_coords = pygame.mouse.get_pos()
        
        # Usa o centro do jogador como referência
        player_center = self.base_player_rect.center

        dx = self.mouse_coords[0] - player_center[0]
        dy = self.mouse_coords[1] - player_center[1]
        
        self.direction = pygame.Vector2(dx, dy).normalize()
        
        # Rotaciona a imagem do jogador com base na direção
        angle = -math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(self.base_player_image, angle)
        self.rect = self.image.get_rect(center=player_center)

    def draw(self, screen):
        """
        Desenha o jogador na tela.
        """
        screen.blit(self.image, self.rect.topleft)

