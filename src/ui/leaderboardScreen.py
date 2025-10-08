"""
Tela do Leaderboard - Mostra os melhores tempos dos jogadores
"""
import pygame
import sys
import os
from src.core.leaderboard import Leaderboard
from src.core.screenUtils import get_optimal_screen_size, center_window
from src.core.constants import Rendering
from src.core.logging_utils import log_error
from src.ui.ui_components import (
    draw_rounded_background,
    create_particle_system, update_and_draw_particles,
    WHITE, GOLD
)

white = WHITE
black = (0, 0, 0)
gold = GOLD
silver = (192, 192, 192)
bronze = (205, 127, 50)
dark_blue = (20, 20, 30)

class LeaderboardScreen:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = None

        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)

        self.leaderboard = Leaderboard()
        self.particles = create_particle_system(screen_width, screen_height, 50)
        
        base_path = os.path.abspath(os.path.dirname(__file__))
        project_root = os.path.abspath(os.path.join(base_path, "../.."))
        background_path = os.path.join(project_root, 'assets', 'ui', 'menu', 'raking.png')
        
        try:
            self.background = pygame.image.load(background_path)
            self.background = pygame.transform.scale(self.background, (screen_width, screen_height))
        except (FileNotFoundError, pygame.error) as e:
            log_error(f"Erro ao carregar background do ranking", "leaderboard", e)
            self.background = pygame.Surface((screen_width, screen_height))
            self.background.fill(dark_blue)

    def _get_rank_color(self, rank: int) -> tuple:
        if rank == 1:
            return gold
        elif rank == 2:
            return silver
        elif rank == 3:
            return bronze
        else:
            return white

    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))

        update_and_draw_particles(self.particles, screen)

        top_scores = self.leaderboard.get_top_scores(10)

        if not top_scores:
            no_scores = self.font_medium.render("Nenhum recorde ainda!", True, white)
            no_scores_rect = no_scores.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            draw_rounded_background(screen, no_scores_rect, (0, 0, 0, 128), 10)
            screen.blit(no_scores, no_scores_rect)
        else:
            start_y = 150
            for i, entry in enumerate(top_scores):
                rank = i + 1
                color = self._get_rank_color(rank)

                score_text = f"{rank:2d}. {entry.name:15s} - {entry.get_time_formatted()}"
                score_surface = self.font_medium.render(score_text, True, color)
                score_rect = score_surface.get_rect(center=(self.screen_width // 2, start_y + (i * 45)))

                draw_rounded_background(screen, score_rect, (0, 0, 0, 100), 10)
                screen.blit(score_surface, score_rect)

        instructions = self.font_small.render("ESC: Voltar ao Menu | R: Resetar Ranking", True, (200, 200, 200))
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        draw_rounded_background(screen, instructions_rect, (0, 0, 0, 100), 5)
        screen.blit(instructions, instructions_rect)

        pygame.display.flip()

def run_leaderboard_screen(screen_width: int, screen_height: int) -> str:
    pygame.init()

    center_window(screen_width, screen_height)
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ranking - Linha Direta")

    leaderboard_screen = LeaderboardScreen(screen_width, screen_height)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                elif event.key == pygame.K_r:
                    leaderboard_screen.leaderboard.clear_scores()

        leaderboard_screen.draw(screen)
        clock.tick(Rendering.TARGET_FPS)

if __name__ == "__main__":
    width, height = get_optimal_screen_size()
    action = run_leaderboard_screen(width, height)
