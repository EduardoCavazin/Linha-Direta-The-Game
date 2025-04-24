import os
import pygame
from typing import Tuple, Any
from src.model.objects.gameObject import GameObject
from src.core.utils import load_image

class Item(GameObject):
    def __init__(self, id: str, name: str, position: Tuple[float, float], size: Tuple[int, int], effect: str) -> None:
        super().__init__(id, position, size)
        self.name: str = name
        self.effect: str = effect
        
        # Usar a função utilitária para carregar a imagem
        self.image = load_image(f"{self.id}.png", size)
        
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
