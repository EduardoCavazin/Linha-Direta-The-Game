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
            sprite_name = f"assets/sprites/{self.id}.png"

        print(f"Tentando carregar sprite: {sprite_name}") 
        
        try:
            self.image = load_image(sprite_name, size)
            print(f"Sprite carregada com sucesso: {sprite_name}")
        except Exception as e:
            print(f"Erro ao carregar sprite {sprite_name}: {e}")

    
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
        if hasattr(self, 'image') and self.image is not None:
            print(f"Desenhando item {self.name} - Imagem: {self.image.get_size()}")
            screen.blit(self.image, self.hitbox.topleft)
        else:
            print(f"ERRO: Item {self.name} não tem imagem válida!")
            pygame.draw.rect(screen, (255, 0, 255), self.hitbox, 2)
