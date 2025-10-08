import sys
import pygame
import os
from src.core.screenUtils import get_optimal_screen_size, center_window
from src.core.logging_utils import log_error
from src.ui.ui_components import (
    create_particle_system, update_and_draw_particles,
    draw_rounded_background, MenuItem, WHITE
)

pygame.init()

screen_width, screen_height = get_optimal_screen_size(preferred_width=950, preferred_height=800)

center_window(screen_width, screen_height)
screen: pygame.Surface = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Menu Principal - Linha Direta")

white: tuple = WHITE
black: tuple = (0, 0, 0)
hover_color: tuple = (100, 200, 255)
selected_color: tuple = (255, 220, 100)

base_path = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(base_path, "../.."))
font_path: str = os.path.join(project_root, 'assets', 'fonts', 'Neutrons.ttf')
background_path: str = os.path.join(project_root, 'assets', 'ui', 'menu', 'background.png')

try:
    font: pygame.font.Font = pygame.font.Font(None, 74)  
except (FileNotFoundError, pygame.error) as e:
    log_error(f"Erro ao carregar fonte", "menu", e)
    font: pygame.font.Font = pygame.font.Font(None, 74) 

try:
    background: pygame.Surface = pygame.image.load(background_path)
    background = pygame.transform.scale(background, (screen_width, screen_height))
except (FileNotFoundError, pygame.error) as e:
    log_error(f"Erro ao carregar background", "menu", e)
    background: pygame.Surface = pygame.Surface((screen_width, screen_height))
    background.fill((50, 50, 75))

start_rect = None
leaderboard_rect = None
credits_rect = None
exit_rect = None

particles = create_particle_system(screen_width, screen_height, 50)

menu_items = []

def show_menu(mouse_pos, dt) -> None:
    global start_rect, leaderboard_rect, credits_rect, exit_rect, menu_items

    screen.blit(background, (0, 0))

    update_and_draw_particles(particles, screen)

    if not menu_items:
        start_rect = pygame.Rect(0, 0, 200, 60)
        start_rect.center = (screen_width // 2, screen_height // 2 - 80)
        leaderboard_rect = pygame.Rect(0, 0, 200, 60)
        leaderboard_rect.center = (screen_width // 2, screen_height // 2)
        credits_rect = pygame.Rect(0, 0, 200, 60)
        credits_rect.center = (screen_width // 2, screen_height // 2 + 80)
        exit_rect = pygame.Rect(0, 0, 200, 60)
        exit_rect.center = (screen_width // 2, screen_height // 2 + 160)

        menu_items.append(MenuItem("Iniciar", start_rect, "start"))
        menu_items.append(MenuItem("Ranking", leaderboard_rect, "leaderboard"))
        menu_items.append(MenuItem("Créditos", credits_rect, "credits"))
        menu_items.append(MenuItem("Sair", exit_rect, "exit"))

    for item in menu_items:
        is_hovered = item.rect.collidepoint(mouse_pos)
        item.update(is_hovered, dt)
        new_rect = item.draw(screen, font, white)

        if item.action == "start":
            start_rect = new_rect
        elif item.action == "leaderboard":
            leaderboard_rect = new_rect
        elif item.action == "credits":
            credits_rect = new_rect
        elif item.action == "exit":
            exit_rect = new_rect

    small_font = pygame.font.Font(None, 36)
    instructions = small_font.render("ENTER: Iniciar | L: Ranking | C: Créditos | ESC: Sair", True, (200, 200, 200))
    instructions_rect = instructions.get_rect(center=(screen_width // 2, screen_height // 2 + 220))
    draw_rounded_background(screen, instructions_rect, (0, 0, 0, 100), 5)
    screen.blit(instructions, instructions_rect)

    pygame.display.flip()
    return None

def run_menu() -> str:
    clock: pygame.time.Clock = pygame.time.Clock()
    dt = 0
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "start"
                elif event.key == pygame.K_l:
                    return "leaderboard"
                elif event.key == pygame.K_c:
                    return "credits"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if start_rect and start_rect.collidepoint(x, y):
                    return "start"
                elif leaderboard_rect and leaderboard_rect.collidepoint(x, y):
                    return "leaderboard"
                elif credits_rect and credits_rect.collidepoint(x, y):
                    return "credits"
                elif exit_rect and exit_rect.collidepoint(x, y):
                    pygame.quit()
                    sys.exit()

        show_menu(mouse_pos, dt)
        dt = clock.tick(60) / 1000.0

def main() -> None:
    action = run_menu()
    if action == "start":
        pass
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
