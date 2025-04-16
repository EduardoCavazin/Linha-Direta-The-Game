import pygame
import sys
import os
from typing import List, Optional

from src.model.entities.enemy import Enemy
from src.ui.hud import Hud
from src.world.map import Map

# Adiciona o diretório 'src' ao PYTHONPATH para facilitar as importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

pygame.init()

WIDTH: int = 800
HEIGHT: int = 600
screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Linha Direta - The Game")
clock: pygame.time.Clock = pygame.time.Clock()

# Carrega o mapa a partir do arquivo JSON
game_map: Map = Map("src/world/map_test.json")
game_map.generate_seed(1)  # Gera uma sequência com 1 sala normal + 1 sala de chefe
room = game_map.current_room
player = room.player

# Lista para armazenar os projéteis
bullets: List = []

# Inicialmente, desenha os elementos estáticos da sala (inimigos, itens, portas)
for enemy in room.enemies:
    enemy.update(player.position)
    enemy.draw(screen)

for item in room.items:
    pygame.draw.rect(screen, (0, 255, 0), item.hitbox)

for door in room.doors:
    pygame.draw.rect(screen, (100, 100, 255), door.hitbox)

# Cria a HUD
hud: Hud = Hud(screen, player)

running: bool = True
while running:
    delta_time: float = clock.tick(60) / 1000.0  # Tempo decorrido entre os frames (em segundos)
    screen.fill((0, 0, 0))  # Limpa a tela

    # Processa os eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Botão esquerdo do mouse
            bullet = player.shoot()  # Presume que o método shoot() retorna um bullet ou None
            if bullet:
                bullets.append(bullet)

    # Processa inputs para o movimento do jogador
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move("up", delta_time, screen_width=WIDTH, screen_height=HEIGHT)
    if keys[pygame.K_s]:
        player.move("down", delta_time, screen_width=WIDTH, screen_height=HEIGHT)
    if keys[pygame.K_a]:
        player.move("left", delta_time, screen_width=WIDTH, screen_height=HEIGHT)
    if keys[pygame.K_d]:
        player.move("right", delta_time, screen_width=WIDTH, screen_height=HEIGHT)

    # Atualiza a rotação do jogador com base na posição do mouse
    player.calculate_rotation()

    # Atualiza e desenha os projéteis
    for bullet in bullets[:]:
        if not bullet.update(delta_time, screen_width=WIDTH, screen_height=HEIGHT):
            bullets.remove(bullet)
        bullet.draw(screen)

    # Atualiza o inimigo (com base na posição do player)
    enemy.update(player.position)

    # Desenha o player e o enemy
    player.draw(screen)
    enemy.draw(screen)

    # Desenha as portas
    for door in room.doors:
        pygame.draw.rect(screen, (100, 100, 255), door.hitbox)
    
    # Desenha os itens e verifica colisão com o player
    for item in room.items:
        pygame.draw.rect(screen, (0, 255, 0), item.hitbox)

    for item in room.items[:]:
        if player.hitbox.colliderect(item.hitbox):
            item.use(player)
            room.items.remove(item)
            print(f"Usou {item.name}!")

    # Verifica colisões do player com portas para mudar de sala
    new_room = room.check_player_door_collision(game_map)
    if new_room != room:
        room = new_room
        player = room.player
        hud.player = player

    hud.player = player
    hud.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
