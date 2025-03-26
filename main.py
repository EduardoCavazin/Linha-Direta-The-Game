import pygame
from pygame.locals import *
from sys import exit
from src.ui.hud import Hud
from src.model.entities.player import Player

pygame.init()

height = 600
width = 800

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Linha Direta")

player = Player(
    id=1,
    name="Player1",
    position=(100, 100),
    size=(50, 50),
    speed=5,
    health=100,
    weapon="Pistol",
    ammo=30,
    status="Alive"
)

hud = Hud(screen, player)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    player.health = 90 
    player.ammo = 25   

    screen.fill((0, 0, 0))

    player.draw(screen)

    hud.draw()

    pygame.display.update()