import pygame
from typing import Any

class Hud:
    def __init__(self, screen: pygame.Surface, player: Any) -> None:
        self.screen: pygame.Surface = screen
        self.player: Any = player
        self.font: pygame.font.Font = pygame.font.Font(None, 36)

    def draw(self) -> None:
        health_text: pygame.Surface = self.font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 10))

        ammo_text: pygame.Surface = self.font.render(f"Ammo: {self.player.ammo}", True, (255, 255, 255))
        self.screen.blit(ammo_text, (10, 50))
