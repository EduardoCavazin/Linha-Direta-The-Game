import pygame
from pygame.locals import *
from sys import exit
from src.ui.hud import Hud
from src.model.entities.player import Player

pygame.init()

height = 600
width = 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Linha Direta - Teste de Movimentação")

black = (0, 0, 0)
red = (255, 0, 0)  

player = Player(
    id=1,
    name="Player1",
    position=(100, 100),
    size=(50, 50),
    speed=5,
    health=100,
    weapon=None,
    ammo=0,
    status="alive"
)

enemy = pygame.Rect(300, 300, 50, 50) 

hud = Hud(screen, player)

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    keys = pygame.key.get_pressed()
    if keys[K_UP]:
        player.move("up")
    if keys[K_DOWN]:
        player.move("down")
    if keys[K_LEFT]:
        player.move("left")
    if keys[K_RIGHT]:
        player.move("right")

    if player.hitbox.colliderect(enemy):
        print("Colisão detectada com o inimigo!")

    screen.fill(black)  # Fundo preto
    player.draw(screen)  # Desenha o jogador
    pygame.draw.rect(screen, red, enemy)  # Desenha o inimigo
    hud.draw()  # Desenha o HUD
    pygame.display.update()

    # Controle de FPS
    clock.tick(60)