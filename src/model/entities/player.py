import math
import pygame
from src.model.entities.entity import Entity

class Player(Entity):
    def __init__(self, id, name, position, size, speed, health, weapon, ammo, status):
        # Converte o centro desejado para o canto superior esquerdo
        topleft = (position[0] - size[0] // 2, position[1] - size[1] // 2)
        
        self.base_player_image = pygame.image.load('assets/sprites/player.png')
        self.base_player_image = pygame.transform.scale(self.base_player_image, size)
        self.base_player_rect = self.base_player_image.get_rect(topleft=topleft)
        
        self.image = self.base_player_image
        self.rect = self.image.get_rect(topleft=topleft)
        self.direction = pygame.Vector2(0, 1)
        
        # Chama o construtor da superclasse usando 'topleft' como posição
        super().__init__(id, name, topleft, size, speed, health, weapon, ammo, self.image, status)
        
        # Garanta que _position esteja corretamente definido (não sobrescreva a propriedade)
        self._position = pygame.Vector2(topleft)
        
    @property
    def position(self) -> pygame.Vector2:
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = pygame.Vector2(value)
    
    def move(self, direction, delta_time, obstacles=None, screen_width=800, screen_height=600):
        super().move(direction, delta_time, obstacles, screen_width, screen_height)
        self.base_player_rect.topleft = (self.position.x, self.position.y)
    
    def reload(self):
        if self.weapon:
            self.ammo = self.weapon.max_ammo

    def player_turning(self):
        self.mouse_coords = pygame.mouse.get_pos()
        # Calcula o centro a partir de base_player_rect
        player_center = (self.position.x + self.size[0] // 2, self.position.y + self.size[1] // 2)
        dx = self.mouse_coords[0] - player_center[0]
        dy = self.mouse_coords[1] - player_center[1]
        self.direction = pygame.Vector2(dx, dy).normalize()
        angle = -math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(self.base_player_image, angle)
        self.rect = self.image.get_rect(center=player_center)
    
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
