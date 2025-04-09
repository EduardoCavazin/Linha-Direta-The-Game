import pygame
import sys
import os

from src.model.entities.enemy import Enemy
from src.ui.hud import Hud
from src.world.map import Map

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Linha Direta - The Game")
clock = pygame.time.Clock()

game_map = Map("src/world/map_test.json")
game_map.generate_seed(1) 
room = game_map.current_room
player = room.player

# Instancia um inimigo à direita do jogador
enemy = Enemy(
    id="enemy_1",
    name="Enemy",
    position=pygame.Vector2(player.position.x + 100, player.position.y),  # 100 pixels à direita do jogador
    size=(50, 50),  # Tamanho do inimigo
    speed=2,
    health=100,
    weapon=None,
    ammo=0,
    status="alive"
)

# HUD
hud = Hud(screen, player)

running = True
while running:
    delta_time = clock.tick(60) / 1000.0
    screen.fill((0, 0, 0))
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move("up", delta_time, screen_width=WIDTH, screen_height=HEIGHT)
    if keys[pygame.K_s]:
        player.move("down", delta_time, screen_width=WIDTH, screen_height=HEIGHT)
    if keys[pygame.K_a]:
        player.move("left", delta_time, screen_width=WIDTH, screen_height=HEIGHT)
    if keys[pygame.K_d]:
        player.move("right", delta_time, screen_width=WIDTH, screen_height=HEIGHT)

    player.player_turning()

    enemy.update(player.position)

    player.draw(screen)
    enemy.draw(screen)

    for item in room.items:
        pygame.draw.rect(screen, (0, 255, 0), item.hitbox)

    for item in room.items[:]:
        if player.hitbox.colliderect(item.hitbox):
            item.use(player)
            room.items.remove(item)
            print(f"Usou {item.name}!")

    hud.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
