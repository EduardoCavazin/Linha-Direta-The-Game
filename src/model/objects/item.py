import os
import pygame
from typing import Tuple, Any
from src.model.objects.gameObject import GameObject
from src.core.utils import load_image

class Item(GameObject):
    def __init__(self, id: str, name: str, position: Tuple[float, float], size: Tuple[int, int], effect: str, sprite_name: str = None) -> None:
        super().__init__(id, position, size)
        self.name: str = name
        self.effect: str = effect
        self.value: int = 0 
        
        if sprite_name is None:
            sprite_name = f"sprites/{self.id}.png"
        
        try:
            self.image = load_image(sprite_name, size)
        except Exception as e:
            try:
                fallback_sprite = "sprites/player.png" if "health" in sprite_name.lower() else "sprites/ammo.png"
                self.image = load_image(fallback_sprite, size)
            except:
                self.image = pygame.Surface(size, pygame.SRCALPHA)
                color = (0, 255, 0) if "health" in sprite_name.lower() else (0, 100, 255) 
                pygame.draw.circle(self.image, color, (size[0]//2, size[1]//2), min(size)//2)
    
    @property
    def position(self) -> Tuple[float, float]:
        return (self._position.x, self._position.y)
    
    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        self._position = pygame.Vector2(value)
        self.hitbox.x, self.hitbox.y = value
        
    def use(self, target: Any) -> None:
        if self.effect == "heal":
            target.health += 20
            if target.health > 100:
                target.health = 100
        elif self.effect == "ammo":
            if target.weapon is not None:
                target.ammo = min(target.ammo + 10, target.weapon.max_ammo)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.hitbox.topleft)
