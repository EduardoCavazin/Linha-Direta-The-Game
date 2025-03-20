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

player = Player(
    name="Player1",
    position=(100, 100),
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

    player.health = 100 
    player.ammo = 30   

    screen.fill((0, 0, 0))

    hud.draw()

    pygame.display.update()