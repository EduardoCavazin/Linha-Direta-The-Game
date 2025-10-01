import sys
import pygame
import os
from src.core.screenUtils import get_optimal_screen_size, center_window
from src.core.logging_utils import log_error

pygame.init()

screen_width, screen_height = get_optimal_screen_size(preferred_width=950, preferred_height=800)

center_window(screen_width, screen_height)
screen: pygame.Surface = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Menu Principal - Linha Direta")

white: tuple = (255, 255, 255)
black: tuple = (0, 0, 0)

base_path = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(base_path, "../.."))
font_path: str = os.path.join(project_root, 'assets', 'fonts', 'Neutrons.ttf')
background_path: str = os.path.join(project_root, 'assets', 'ui', 'menu', 'background.png')

try:
    font: pygame.font.Font = pygame.font.Font(font_path, 74)
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

title_rect = None
start_rect = None
leaderboard_rect = None
exit_rect = None

def draw_rounded_background(surface: pygame.Surface, rect: pygame.Rect, color: tuple, radius: int) -> None:
    transparent_background: pygame.Surface = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(transparent_background, color, transparent_background.get_rect(), border_radius=radius)
    surface.blit(transparent_background, (rect.x - 10, rect.y - 5))

def show_menu() -> None:
    global title_rect, start_rect, leaderboard_rect, exit_rect

    screen.blit(background, (0, 0))

    title: pygame.Surface = font.render("Linha Direta", True, white)
    start: pygame.Surface = font.render("Iniciar", True, white)
    leaderboard: pygame.Surface = font.render("Ranking", True, white)
    exit: pygame.Surface = font.render("Sair", True, white)

    small_font = pygame.font.Font(None, 36)
    instructions = small_font.render("ENTER: Iniciar | L: Ranking | ESC: Sair", True, (200, 200, 200))

    title_rect = title.get_rect(center=(screen_width // 2, screen_height // 2 - 200))
    start_rect = start.get_rect(center=(screen_width // 2, screen_height // 2 - 80))
    leaderboard_rect = leaderboard.get_rect(center=(screen_width // 2, screen_height // 2))
    exit_rect = exit.get_rect(center=(screen_width // 2, screen_height // 2 + 80))
    instructions_rect = instructions.get_rect(center=(screen_width // 2, screen_height // 2 + 220))

    for rect in [title_rect, start_rect, leaderboard_rect, exit_rect]:
        draw_rounded_background(screen, rect, (0, 0, 0, 128), 10)
    draw_rounded_background(screen, instructions_rect, (0, 0, 0, 100), 5)

    screen.blit(title, title_rect)
    screen.blit(start, start_rect)
    screen.blit(leaderboard, leaderboard_rect)
    screen.blit(exit, exit_rect)
    screen.blit(instructions, instructions_rect)

    pygame.display.flip()
    return None

def run_menu() -> str:
    clock: pygame.time.Clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "start"
                elif event.key == pygame.K_l:
                    return "leaderboard"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if start_rect and start_rect.collidepoint(x, y):
                    return "start"
                elif leaderboard_rect and leaderboard_rect.collidepoint(x, y):
                    return "leaderboard"
                elif exit_rect and exit_rect.collidepoint(x, y):
                    pygame.quit()
                    sys.exit()

        show_menu()
        clock.tick(10)

def main() -> None:
    action = run_menu()
    if action == "start":
        pass
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
