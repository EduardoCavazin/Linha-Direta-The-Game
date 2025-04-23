import pygame
from typing import Any

class Hud:
    def __init__(self, screen: pygame.Surface, player: Any, clock: pygame.time.Clock) -> None:
        self.screen: pygame.Surface = screen
        self.player: Any = player
        self.clock: pygame.time.Clock = clock
        self.font: pygame.font.Font = pygame.font.Font(None, 36)

    def draw(self) -> None:
        # Exibe vida e munição
        health_text: pygame.Surface = self.font.render(
            f"Health: {self.player.health}", True, (255, 255, 255)
        )
        self.screen.blit(health_text, (10, 10))

        ammo_text: pygame.Surface = self.font.render(
            f"Ammo: {self.player.ammo}", True, (255, 255, 255)
        )
        self.screen.blit(ammo_text, (10, 50))

        # Exibe FPS no canto superior direito
        fps: int = int(self.clock.get_fps())
        fps_text: pygame.Surface = self.font.render(
            f"FPS: {fps}", True, (255, 255, 255)
        )
        # posiciona 10px da borda direita
        x = self.screen.get_width() - fps_text.get_width() - 10
        y = 10
        self.screen.blit(fps_text, (x, y))
