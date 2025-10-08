"""
Game Over Screen - Displayed when player dies
"""
import pygame
import math
from typing import Callable, List
from src.core.enums import GameState
from src.core.leaderboard import Leaderboard, LeaderboardEntry
from src.ui.ui_components import (
    MenuItem, draw_rounded_background, draw_pulsing_title,
    create_particle_system, update_and_draw_particles,
    WHITE, GOLD, SELECTED_COLOR
)

class GameOverScreen:
    def __init__(self, screen: pygame.Surface, game_completed: bool = False):
        self.screen = screen
        self.game_completed = game_completed
        self.leaderboard = Leaderboard()
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)

        # Colors
        self.background_color = (20, 20, 30)
        self.text_color = WHITE
        self.red_accent = (200, 50, 50)

        self.button_width = 300
        self.button_height = 60
        self.button_spacing = 20

        self.center_x = screen.get_width() // 2
        self.center_y = screen.get_height() // 2

        # Partículas
        self.particles = create_particle_system(screen.get_width(), screen.get_height(), 50)

        # Menu items animados
        self.menu_items = []
        restart_rect = pygame.Rect(0, 0, self.button_width, self.button_height)
        restart_rect.center = (self.center_x, self.center_y + 50)
        self.menu_items.append(MenuItem("Reiniciar (R)", restart_rect, "restart"))

        credits_rect = pygame.Rect(0, 0, self.button_width, self.button_height)
        credits_rect.center = (self.center_x, self.center_y + 50 + self.button_height + self.button_spacing)
        self.menu_items.append(MenuItem("Créditos (C)", credits_rect, "credits"))

        quit_rect = pygame.Rect(0, 0, self.button_width, self.button_height)
        quit_rect.center = (self.center_x, self.center_y + 50 + 2 * (self.button_height + self.button_spacing))
        self.menu_items.append(MenuItem("Sair (ESC)", quit_rect, "quit"))

        self.restart_button = restart_rect
        self.credits_button = credits_rect
        self.quit_button = quit_rect

        self.dt = 0
    
    def handle_mouse_motion(self, mouse_pos: tuple) -> None:
        pass  # Agora é gerenciado pelos MenuItems
    
    def handle_click(self, mouse_pos: tuple) -> str:
        if self.restart_button.collidepoint(mouse_pos):
            return "restart"
        elif self.credits_button.collidepoint(mouse_pos):
            return "credits"
        elif self.quit_button.collidepoint(mouse_pos):
            return "quit"
        return "none"
    
    def handle_keypress(self, key: int) -> str:
        if key == pygame.K_r:
            return "restart"
        elif key == pygame.K_c:
            return "credits"
        elif key == pygame.K_ESCAPE:
            return "quit"
        return "none"
    
    def draw(self, mouse_pos: tuple = None, dt: float = 0.016) -> None:
        self.screen.fill(self.background_color)

        # Partículas
        update_and_draw_particles(self.particles, self.screen)

        # Título com efeito
        if self.game_completed:
            draw_pulsing_title(self.screen, "PARABÉNS!", 74, (self.center_x, 80), (0, 255, 0))
            subtitle_text = self.font_medium.render("Você completou todos os mapas!", True, self.text_color)
        else:
            draw_pulsing_title(self.screen, "GAME OVER", 74, (self.center_x, 80), self.red_accent)
            subtitle_text = self.font_medium.render("Você foi eliminado!", True, self.text_color)

        subtitle_rect = subtitle_text.get_rect(center=(self.center_x, 140))
        draw_rounded_background(self.screen, subtitle_rect, (0, 0, 0, 128), 10)
        self.screen.blit(subtitle_text, subtitle_rect)

        self._draw_leaderboard()

        # Atualizar e desenhar menu items
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        for item in self.menu_items:
            is_hovered = item.rect.collidepoint(mouse_pos)
            item.update(is_hovered, dt)
            new_rect = item.draw(self.screen, self.font_small, self.text_color)

            # Atualizar rects para detecção de clique
            if item.action == "restart":
                self.restart_button = new_rect
            elif item.action == "credits":
                self.credits_button = new_rect
            elif item.action == "quit":
                self.quit_button = new_rect

        instruction_text = self.font_small.render("R - Reiniciar | C - Créditos | ESC - Sair", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(self.center_x, self.screen.get_height() - 50))
        draw_rounded_background(self.screen, instruction_rect, (0, 0, 0, 100), 5)
        self.screen.blit(instruction_text, instruction_rect)
    
    def _draw_leaderboard(self) -> None:
        if not self.game_completed:
            message_text = self.font_small.render("Complete todos os mapas para entrar no ranking!", True, (255, 255, 0))
            message_rect = message_text.get_rect(center=(self.center_x, 200))
            draw_rounded_background(self.screen, message_rect, (0, 0, 0, 120), 10)
            self.screen.blit(message_text, message_rect)
            return

        leaderboard_title = self.font_medium.render("TOP 5 MELHORES TEMPOS", True, GOLD)
        title_rect = leaderboard_title.get_rect(center=(self.center_x, 190))
        draw_rounded_background(self.screen, title_rect, (0, 0, 0, 140), 10)
        self.screen.blit(leaderboard_title, title_rect)

        top_scores = self.leaderboard.get_top_scores(5)

        if not top_scores:
            no_scores_text = self.font_small.render("Nenhum recorde ainda!", True, self.text_color)
            no_scores_rect = no_scores_text.get_rect(center=(self.center_x, 230))
            draw_rounded_background(self.screen, no_scores_rect, (0, 0, 0, 120), 10)
            self.screen.blit(no_scores_text, no_scores_rect)
            return

        start_y = 240
        for i, entry in enumerate(top_scores):
            rank = i + 1
            color = self._get_rank_color(rank)

            score_text = f"{rank}. {entry.name} - {entry.get_time_formatted()}"

            score_surface = self.font_small.render(score_text, True, color)
            score_rect = score_surface.get_rect(center=(self.center_x, start_y + (i * 35)))
            draw_rounded_background(self.screen, score_rect, (0, 0, 0, 100), 8)
            self.screen.blit(score_surface, score_rect)
    
    def _get_rank_color(self, rank: int) -> tuple:
        if rank == 1:
            return (255, 215, 0)  
        elif rank == 2:
            return (192, 192, 192) 
        elif rank == 3:
            return (205, 127, 50) 
        else:
            return (255, 255, 255)  
