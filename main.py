import pygame
import sys
import os
from typing import List

from src.ui.hud import Hud
from src.world.map import Map

pygame.init()

WIDTH: int = 1280
HEIGHT: int = 720
screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Linha Direta - The Game")
clock: pygame.time.Clock = pygame.time.Clock()

# Carrega as salas a partir da pasta de XMLs
game_map: Map = Map("src/world/rooms")
game_map.generate_seed(1)
room = game_map.current_room
player = room.player

# Lista de balas disparadas
bullets: List = []

# HUD (exibição de vida e munição)
hud: Hud = Hud(screen, player, clock)

running: bool = True
while running:
    delta_time: float = clock.tick(60) / 1000.0
    
    # Eventos de entrada
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            bullet = player.shoot()
            if bullet:
                bullets.append(bullet)

    # Movimento do jogador com colisão opcional contra inimigos
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move("up", delta_time, obstacles=room.enemies, screen_width=WIDTH, screen_height=HEIGHT)
    if keys[pygame.K_s]:
        player.move("down", delta_time, obstacles=room.enemies, screen_width=WIDTH, screen_height=HEIGHT)
    if keys[pygame.K_a]:
        player.move("left", delta_time, obstacles=room.enemies, screen_width=WIDTH, screen_height=HEIGHT)
    if keys[pygame.K_d]:
        player.move("right", delta_time, obstacles=room.enemies, screen_width=WIDTH, screen_height=HEIGHT)

    # Atualiza rotação do jogador
    player.calculate_rotation()

    # Atualiza balas (movimentação e remoção fora da tela)
    for b in bullets[:]:
        if not b.update(delta_time, screen_width=WIDTH, screen_height=HEIGHT):
            bullets.remove(b)

    # Colisões bala ↔ inimigo
    room.handle_bullet_collisions(bullets)

    # --- Fila de renderização ---
    render_queue: List = []

    # Enfileira inimigos vivos
    for enemy in room.enemies[:]:
        if not enemy.is_alive():
            room.enemies.remove(enemy)
            print(f"{enemy.name} foi derrotado!")
        else:
            enemy.update(player.position)
            render_queue.append(enemy)

    # Enfileira balas
    for b in bullets:
        render_queue.append(b)

    # Enfileira o player para desenhar sobre as balas e inimigos
    render_queue.append(player)

    # Limpa tela e desenha tudo na ordem da fila
    screen.blit(room.background, (0, 0))
    for obj in render_queue:
        obj.draw(screen)

    # Desenha portas e itens (hitboxes)
    for door in room.doors:
        pygame.draw.rect(screen, (100, 100, 255), door.hitbox)
    for item in room.items:
        item.draw(screen)


    # Coleta de itens
    for item in room.items[:]:
        if player.hitbox.colliderect(item.hitbox):
            item.use(player)
            room.items.remove(item)
            print(f"Usou {item.name}!")

    # Troca de sala ao colidir com porta
    new_room = room.check_player_door_collision(game_map)
    if new_room is not room:
        room = new_room
        player = room.player
        hud.player = player

    # Desenha HUD e atualiza display
    hud.draw()
    pygame.display.flip()

pygame.quit()
sys.exit()
