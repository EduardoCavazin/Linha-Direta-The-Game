import math
import pygame
from src.model.entities.entity import Entity

class Player(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        # Aqui, 'position' já é considerado o canto superior esquerdo
        self.base_player_image = pygame.image.load('assets/sprites/player.png')
        self.base_player_image = pygame.transform.scale(self.base_player_image, size)
        self.base_player_rect = self.base_player_image.get_rect(topleft=position)
        
        self.image = self.base_player_image
        self.rect = self.image.get_rect(topleft=position)
        
        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)
    
    def move(self, direction, delta_time, obstacles=None, screen_width=800, screen_height=600):
        super().move(direction, delta_time, obstacles, screen_width, screen_height)
        self.base_player_rect.topleft = (self.position.x, self.position.y)
    
    def reload(self):
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def player_turning(self):
        mouse_coords = pygame.mouse.get_pos()
        # Calcula o centro a partir do canto superior esquerdo e do tamanho
        player_center = (self.position.x + self.size[0] // 2, self.position.y + self.size[1] // 2)
        dx = mouse_coords[0] - player_center[0]
        dy = mouse_coords[1] - player_center[1]
        self.angle = int(math.degrees(math.atan2(dy, dx))) % 360
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(topleft=self.position)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
