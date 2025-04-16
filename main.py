import pygame
import sys
import os
from typing import List, Optional

from src.model.entities.enemy import Enemy
from src.ui.hud import Hud
from src.world.map import Map


pygame.init()

WIDTH: int = 800
HEIGHT: int = 600
screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Linha Direta - The Game")
clock: pygame.time.Clock = pygame.time.Clock()

game_map: Map = Map("src/world/rooms")
game_map.generate_seed(1)  
room = game_map.current_room
player = room.player

bullets: List = []

for enemy in room.enemies:
    enemy.update(player.position)
    enemy.draw(screen)

for item in room.items:
    pygame.draw.rect(screen, (0, 255, 0), item.hitbox)

for door in room.doors:
    pygame.draw.rect(screen, (100, 100, 255), door.hitbox)

hud: Hud = Hud(screen, player)

running: bool = True
while running:
    delta_time: float = clock.tick(60) / 1000.0  
    screen.fill((0, 0, 0))  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            bullet = player.shoot()  
            if bullet:
                bullets.append(bullet)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move("up", 
                    delta_time,
                    obstacles = room.enemies, 
                    screen_width=WIDTH, 
                    screen_height=HEIGHT)
    if keys[pygame.K_s]:
        player.move("down", 
                    delta_time,
                    obstacles = room.enemies, 
                    screen_width=WIDTH, 
                    screen_height=HEIGHT)
    if keys[pygame.K_a]:
        player.move("left", 
                    delta_time,
                    obstacles = room.enemies, 
                    screen_width=WIDTH, 
                    screen_height=HEIGHT)
    if keys[pygame.K_d]:
        player.move("right", 
                    delta_time,
                    obstacles = room.enemies, 
                    screen_width=WIDTH, 
                    screen_height=HEIGHT)

    player.calculate_rotation()

    for bullet in bullets[:]:
        if not bullet.update(delta_time, screen_width=WIDTH, screen_height=HEIGHT):
            bullets.remove(bullet)
        bullet.draw(screen)

    enemy.update(player.position)

    player.draw(screen)
    enemy.draw(screen)

    for door in room.doors:
        pygame.draw.rect(screen, (100, 100, 255), door.hitbox)
    
    for item in room.items:
        pygame.draw.rect(screen, (0, 255, 0), item.hitbox)

    for item in room.items[:]:
        if player.hitbox.colliderect(item.hitbox):
            item.use(player)
            room.items.remove(item)
            print(f"Usou {item.name}!")

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
