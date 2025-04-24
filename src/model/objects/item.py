import pygame
from typing import Tuple, Any
from src.model.objects.gameObject import GameObject

class Item(GameObject):
    def __init__(self, id: str, name: str, position: Tuple[float, float], size: Tuple[int, int], effect: str) -> None:
        super().__init__(id, position, size)
        self.name: str = name
        self.effect: str = effect
        self.image: pygame.Surface = pygame.image.load(f"assets/sprites/{self.id}.png")
        self.image = pygame.transform.scale(self.image, size)

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
