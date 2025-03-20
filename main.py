import pygame
from pygame.locals import *
from sys import exit
from src.ui.hud import Hud
from src.entities.player import Player

pygame.init()

height = 600
width = 800

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Linha Direta")

# Instantiate the player with required arguments
player = Player(
    name="Player1",
    position=(100, 100),
    speed=5,
    health=100,
    weapon="Pistol",
    ammo=30,
    status="Alive"
)

# Instantiate the HUD with the player instance
hud = Hud(screen, player)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    # Update game state (example updates)
    player.health = 90  # Example update
    player.ammo = 25    # Example update

    # Clear screen
    screen.fill((0, 0, 0))

    # Draw player
    player.draw(screen)

    # Draw HUD
    hud.draw()

    # Update display
    pygame.display.update()