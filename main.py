import pygame
import sys
from src.world.map import Map
from src.ui.hud import Hud

pygame.init()

# Configurações de tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Linha Direta - The Game")
clock = pygame.time.Clock()

# Carrega o mapa real do JSON
game_map = Map("src\world\map_test.json")
game_map.generate_seed(1)  # Gera uma sequência com 1 sala + boss

# Acessa a sala atual e o player
room = game_map.current_room
player = room.player

# HUD
hud = Hud(screen, player)

# Loop principal
running = True
while running:
    screen.fill((0, 0, 0))  # Limpa a tela

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input (movimento básico com setas)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move("up")
    if keys[pygame.K_s]:
        player.move("down")
    if keys[pygame.K_a]:
        player.move("left")
    if keys[pygame.K_d]:
        player.move("right")

    # Desenha jogador
    player.draw(screen)

    # Desenha itens da sala
    for item in room.items:
        pygame.draw.rect(screen, (0, 255, 0), item.hitbox)

    # Checa colisão jogador-item
    for item in room.items[:]:
        if player.hitbox.colliderect(item.hitbox):
            item.use(player)
            room.items.remove(item)
            print(f"{player.name} usou {item.name}!")

    # HUD
    hud.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
