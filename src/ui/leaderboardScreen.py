"""
Tela do Leaderboard - Mostra os melhores tempos dos jogadores
"""
import pygame
import sys
from src.core.leaderboard import Leaderboard
from src.core.screenUtils import get_optimal_screen_size, center_window

# Cores
white = (255, 255, 255)
black = (0, 0, 0)
gold = (255, 215, 0)
silver = (192, 192, 192)
bronze = (205, 127, 50)
dark_blue = (20, 20, 30)

class LeaderboardScreen:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = None  # Sera inicializado quando necessario

        # Carregar fonte
        try:
            self.font_large = pygame.font.Font("assets/fonts/techno_hideo.ttf", 64)
            self.font_medium = pygame.font.Font("assets/fonts/techno_hideo.ttf", 36)
            self.font_small = pygame.font.Font("assets/fonts/techno_hideo.ttf", 28)
        except:
            self.font_large = pygame.font.Font(None, 64)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 28)

        self.leaderboard = Leaderboard()

    def _get_rank_color(self, rank: int) -> tuple:
        """Retorna cor baseada na posicao do ranking"""
        if rank == 1:
            return gold
        elif rank == 2:
            return silver
        elif rank == 3:
            return bronze
        else:
            return white

    def _draw_rounded_background(self, surface: pygame.Surface, rect: pygame.Rect, color: tuple, radius: int = 10):
        """Desenha fundo arredondado"""
        transparent_bg = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(transparent_bg, color, transparent_bg.get_rect(), border_radius=radius)
        surface.blit(transparent_bg, (rect.x - 10, rect.y - 5))

    def draw(self, screen: pygame.Surface):
        """Desenha a tela do leaderboard"""
        # Fundo
        screen.fill(dark_blue)

        # Titulo
        title = self.font_large.render("RANKING DOS MELHORES", True, gold)
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        self._draw_rounded_background(screen, title_rect, (0, 0, 0, 128))
        screen.blit(title, title_rect)

        # Obter top scores
        top_scores = self.leaderboard.get_top_scores(10)

        if not top_scores:
            # Nenhum score ainda
            no_scores = self.font_medium.render("Nenhum recorde ainda!", True, white)
            no_scores_rect = no_scores.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self._draw_rounded_background(screen, no_scores_rect, (0, 0, 0, 128))
            screen.blit(no_scores, no_scores_rect)
        else:
            # Desenhar scores
            start_y = 150
            for i, entry in enumerate(top_scores):
                rank = i + 1
                color = self._get_rank_color(rank)

                # Texto do score: "1. Nome - 02:45"
                score_text = f"{rank:2d}. {entry.name:15s} - {entry.get_time_formatted()}"
                score_surface = self.font_medium.render(score_text, True, color)
                score_rect = score_surface.get_rect(center=(self.screen_width // 2, start_y + (i * 45)))

                # Background para score
                self._draw_rounded_background(screen, score_rect, (0, 0, 0, 100))
                screen.blit(score_surface, score_rect)

        # Instrucoes
        instructions = self.font_small.render("ESC: Voltar ao Menu | R: Resetar Ranking", True, (200, 200, 200))
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self._draw_rounded_background(screen, instructions_rect, (0, 0, 0, 100))
        screen.blit(instructions, instructions_rect)

        pygame.display.flip()

def run_leaderboard_screen(screen_width: int, screen_height: int) -> str:
    """
    Executa a tela do leaderboard
    Retorna: 'menu' para voltar ao menu
    """
    pygame.init()

    # Centralizar janela
    center_window(screen_width, screen_height)
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Leaderboard - Linha Direta")

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
                    # Resetar leaderboard
                    leaderboard_screen.leaderboard.clear_scores()
                    # Continuar rodando para mostrar leaderboard vazio

        # Desenhar tela
        leaderboard_screen.draw(screen)
        clock.tick(60)

if __name__ == "__main__":
    # Teste isolado da tela
    width, height = get_optimal_screen_size()
    action = run_leaderboard_screen(width, height)
    print(f"Acao retornada: {action}")