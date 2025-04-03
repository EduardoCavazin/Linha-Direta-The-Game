import pygame
import sys
from src.world.map import Map
from src.ui.hud import Hud
from src.model.entities.enemy import Enemy

pygame.init()

# Configurações de tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Linha Direta - The Game")
clock = pygame.time.Clock()

# Carrega o mapa real do JSON
game_map = Map("src/world/map_test.json")
game_map.generate_seed(1)  # Gera uma sequência com 1 sala + boss

# Acessa a sala atual e o player
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

# Loop principal
running = True
while running:
    delta_time = clock.tick(60) / 1000.0  # Tempo decorrido entre os quadros (em segundos)
    screen.fill((0, 0, 0))  # Limpa a tela

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input (movimento básico com setas)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move("up", delta_time)
    if keys[pygame.K_s]:
        player.move("down", delta_time)
    if keys[pygame.K_a]:
        player.move("left", delta_time)
    if keys[pygame.K_d]:
        player.move("right", delta_time)

    # Atualiza a rotação do jogador com base no mouse
    player.player_turning()

    enemy.update(player.position)

    player.draw(screen)
    enemy.draw(screen)

    # Desenha itens da sala
    for item in room.items:
        pygame.draw.rect(screen, (0, 255, 0), item.hitbox)

    # Checa colisão jogador-item
    for item in room.items[:]:
        if player.hitbox.colliderect(item.hitbox):
            item.use(player)
            room.items.remove(item)
            print(f"Usou {item.name}!")

    # HUD
    hud.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
