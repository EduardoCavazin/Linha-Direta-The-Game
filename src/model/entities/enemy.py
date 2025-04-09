import math
import pygame
from src.model.entities.entity import Entity


class Enemy(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        self.base_enemy_image = pygame.image.load("assets/sprites/player.png")  
        self.base_enemy_image = pygame.transform.scale(self.base_enemy_image, size)
        self.base_enemy_rect = self.base_enemy_image.get_rect(topleft=position)
        
        self.image = self.base_enemy_image
        self.rect = self.image.get_rect(topleft=position)
        
        self.direction = pygame.Vector2(0, 1)
        
        super().__init__(id, name, position, size, speed, health, weapon, ammo, self.image, status)
        
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = pygame.Vector2(value)
    
    def update_rotation(self, player_position):
        direction = pygame.Vector2(player_position.x - self.position.x, player_position.y - self.position.y)
        if direction.length() != 0:
            direction = direction.normalize()
        self.direction = direction
        self.rotation = -math.degrees(math.atan2(direction.y, direction.x))
        
        self.image = pygame.transform.rotate(self.base_enemy_image, self.rotation)
        self.rect = self.image.get_rect(topleft=self.position)
    
    def update(self, player_position):
        self.update_rotation(player_position)
    
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
