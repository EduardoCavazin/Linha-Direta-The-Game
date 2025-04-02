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

        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)
    
    def move(self, direction, delta_time, obstacles=None):
        super().move(direction, delta_time, obstacles)
        self.base_player_rect.center = (self.position.x, self.position.y)
    
    def reload(self):
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def player_turning(self):
        self.mouse_coords = pygame.mouse.get_pos()
        
        player_center = self.base_player_rect.center  
        
        dx = self.mouse_coords[0] - player_center[0]
        dy = self.mouse_coords[1] - player_center[1]
        
        self.angle = int(math.degrees(math.atan2(dy, dx))) % 360
        
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=player_center)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

