import sys
import pygame
import os
import random
import math
from src.core.screenUtils import get_optimal_screen_size, center_window
from src.core.logging_utils import log_error

pygame.init()

screen_width, screen_height = get_optimal_screen_size(preferred_width=950, preferred_height=800)

center_window(screen_width, screen_height)
screen: pygame.Surface = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Menu Principal - Linha Direta")

white: tuple = (255, 255, 255)
black: tuple = (0, 0, 0)
hover_color: tuple = (100, 200, 255)
selected_color: tuple = (255, 220, 100)

base_path = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(base_path, "../.."))
font_path: str = os.path.join(project_root, 'assets', 'fonts', 'Neutrons.ttf')
background_path: str = os.path.join(project_root, 'assets', 'ui', 'menu', 'background.png')

try:
    # font: pygame.font.Font = pygame.font.Font(font_path, 74)
    font: pygame.font.Font = pygame.font.Font(None, 74)  # Teste temporário
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
credits_rect = None
exit_rect = None

class Particle:
    def __init__(self):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(100, 200)

    def update(self):
        self.y += self.speed
        if self.y > screen_height:
            self.y = 0
            self.x = random.randint(0, screen_width)

    def draw(self, surface):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))

particles = [Particle() for _ in range(50)]

class MenuItem:
    def __init__(self, text, rect, action):
        self.text = text
        self.rect = rect
        self.action = action
        self.scale = 1.0
        self.target_scale = 1.0
        self.glow_intensity = 0
        self.pulse_time = 0

    def update(self, is_hovered, dt):
        self.target_scale = 1.15 if is_hovered else 1.0
        self.scale += (self.target_scale - self.scale) * 0.15

        if is_hovered:
            self.glow_intensity = min(255, self.glow_intensity + 15)
            self.pulse_time += dt * 5
        else:
            self.glow_intensity = max(0, self.glow_intensity - 10)
            self.pulse_time = 0

    def draw(self, surface, font, base_color):
        pulse = math.sin(self.pulse_time) * 0.05 + 1 if self.glow_intensity > 0 else 1
        current_scale = self.scale * pulse

        text_surface = font.render(self.text, True, base_color)
        scaled_width = int(text_surface.get_width() * current_scale)
        scaled_height = int(text_surface.get_height() * current_scale)
        scaled_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))

        scaled_rect = scaled_surface.get_rect(center=self.rect.center)

        if self.glow_intensity > 0:
            glow_surface = pygame.Surface((scaled_rect.width + 40, scaled_rect.height + 40), pygame.SRCALPHA)
            glow_color = (*hover_color, int(self.glow_intensity * 0.5))
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=15)
            surface.blit(glow_surface, (scaled_rect.x - 20, scaled_rect.y - 20))

        bg_rect = pygame.Rect(scaled_rect.x - 10, scaled_rect.y - 5,
                              scaled_rect.width + 20, scaled_rect.height + 10)
        alpha_value = 128 + int(self.glow_intensity * 0.3)
        draw_rounded_background(surface, bg_rect, (0, 0, 0, alpha_value), 10)

        surface.blit(scaled_surface, scaled_rect)

        return scaled_rect

menu_items = []

def draw_rounded_background(surface: pygame.Surface, rect: pygame.Rect, color: tuple, radius: int) -> None:
    transparent_background: pygame.Surface = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(transparent_background, color, transparent_background.get_rect(), border_radius=radius)
    surface.blit(transparent_background, (rect.x - 10, rect.y - 5))

def show_menu(mouse_pos, dt) -> None:
    global title_rect, start_rect, leaderboard_rect, credits_rect, exit_rect, menu_items

    screen.blit(background, (0, 0))

    for particle in particles:
        particle.update()
        particle.draw(screen)

    title_pulse = math.sin(pygame.time.get_ticks() * 0.002) * 0.03 + 1
    title_font = pygame.font.Font(None, int(74 * title_pulse))
    title: pygame.Surface = title_font.render("Linha Direta", True, selected_color)
    title_rect = title.get_rect(center=(screen_width // 2, screen_height // 2 - 200))

    title_glow = pygame.Surface((title_rect.width + 60, title_rect.height + 60), pygame.SRCALPHA)
    glow_alpha = int((math.sin(pygame.time.get_ticks() * 0.003) * 0.5 + 0.5) * 100)
    pygame.draw.rect(title_glow, (*selected_color, glow_alpha), title_glow.get_rect(), border_radius=20)
    screen.blit(title_glow, (title_rect.x - 30, title_rect.y - 30))

    draw_rounded_background(screen, title_rect, (0, 0, 0, 150), 10)
    screen.blit(title, title_rect)

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
