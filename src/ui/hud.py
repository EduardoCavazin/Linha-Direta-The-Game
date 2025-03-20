import pygame

class Hud:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.font = pygame.font.Font(None, 36)

    def draw(self):
        # Draw health
        health_text = self.font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 10))

        # Draw ammo
        ammo_text = self.font.render(f"Ammo: {self.player.ammo}", True, (255, 255, 255))
        self.screen.blit(ammo_text, (10, 50))