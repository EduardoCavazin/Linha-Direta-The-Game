import math
import pygame
from src.model.entities.entity import Entity

class Player(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        # Carregar a imagem base do jogador
        self.base_player_image = pygame.image.load('assets/sprites/player.png')
        self.base_player_image = pygame.transform.scale(self.base_player_image, size)
        self.base_player_rect = self.base_player_image.get_rect(center=position)

        # Inicializa a imagem rotacionada
        self.image = self.base_player_image
        self.rect = self.image.get_rect(center=self.base_player_rect.center)

        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)
    
    def move(self, direction, delta_time, obstacles=None):
        super().move(direction, delta_time, obstacles)
        # Atualiza o centro do retângulo base com a nova posição
        self.base_player_rect.center = (self.position.x, self.position.y)
    
    def reload(self):
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def player_turning(self):
        """
        Atualiza a rotação do jogador com base na posição do mouse em relação à posição do jogador.
        """
        # Pega as coordenadas do mouse (em pixels na tela)
        self.mouse_coords = pygame.mouse.get_pos()
        
        # Usa o centro do jogador como referência
        player_center = self.base_player_rect.center  # ou (self.position.x, self.position.y)
        
        # Calcula a diferença entre a posição do mouse e a posição do jogador
        dx = self.mouse_coords[0] - player_center[0]
        dy = self.mouse_coords[1] - player_center[1]
        
        # Calcula o ângulo em graus usando a função atan2
        self.angle = int(math.degrees(math.atan2(dy, dx))) % 360
        
        # Rotaciona a imagem do jogador
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=player_center)

    def draw(self, screen):
        """
        Desenha o jogador na tela.
        """
        screen.blit(self.image, self.rect.topleft)

