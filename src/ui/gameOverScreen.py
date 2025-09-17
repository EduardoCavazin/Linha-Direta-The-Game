"""
Game Over Screen - Displayed when player dies
"""
import pygame
from typing import Callable, List
from src.core.enums import GameState
from src.core.leaderboard import Leaderboard, LeaderboardEntry

class GameOverScreen:
    def __init__(self, screen: pygame.Surface, game_completed: bool = False):
        self.screen = screen
        self.game_completed = game_completed
        self.leaderboard = Leaderboard()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Colors
        self.background_color = (20, 20, 30)  # Dark blue
        self.text_color = (255, 255, 255)     # White
        self.button_color = (60, 60, 80)      # Dark gray
        self.button_hover_color = (80, 80, 100)  # Light gray
        self.red_accent = (200, 50, 50)       # Red for "Game Over"
        
        # Button properties
        self.button_width = 300
        self.button_height = 60
        self.button_spacing = 20
        
        # Center of screen
        self.center_x = screen.get_width() // 2
        self.center_y = screen.get_height() // 2
        
        # Create buttons
        self.restart_button = pygame.Rect(
            self.center_x - self.button_width // 2,
            self.center_y + 50,
            self.button_width,
            self.button_height
        )
        
        self.quit_button = pygame.Rect(
            self.center_x - self.button_width // 2,
            self.center_y + 50 + self.button_height + self.button_spacing,
            self.button_width,
            self.button_height
        )
        
        # Track hover states
        self.restart_hovered = False
        self.quit_hovered = False
    
    def handle_mouse_motion(self, mouse_pos: tuple) -> None:
        """Update button hover states based on mouse position"""
        self.restart_hovered = self.restart_button.collidepoint(mouse_pos)
        self.quit_hovered = self.quit_button.collidepoint(mouse_pos)
    
    def handle_click(self, mouse_pos: tuple) -> str:
        """Handle mouse clicks and return action"""
        if self.restart_button.collidepoint(mouse_pos):
            return "restart"
        elif self.quit_button.collidepoint(mouse_pos):
            return "quit"
        return "none"
    
    def handle_keypress(self, key: int) -> str:
        """Handle keyboard input"""
        if key == pygame.K_r:
            return "restart"
        elif key == pygame.K_ESCAPE or key == pygame.K_q:
            return "quit"
        return "none"
    
    def draw(self) -> None:
        """Draw the game over screen"""
        # Fill background
        self.screen.fill(self.background_color)
        
        # Draw title based on completion status
        if self.game_completed:
            title_text = self.font_large.render("PARABÉNS!", True, (0, 255, 0))  # Green for success
            subtitle_text = self.font_medium.render("Você completou todos os mapas!", True, self.text_color)
        else:
            title_text = self.font_large.render("GAME OVER", True, self.red_accent)
            subtitle_text = self.font_medium.render("You were eliminated!", True, self.text_color)

        title_rect = title_text.get_rect(center=(self.center_x, 80))
        self.screen.blit(title_text, title_rect)

        subtitle_rect = subtitle_text.get_rect(center=(self.center_x, 130))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw leaderboard
        self._draw_leaderboard()
        
        # Draw restart button
        restart_color = self.button_hover_color if self.restart_hovered else self.button_color
        pygame.draw.rect(self.screen, restart_color, self.restart_button)
        pygame.draw.rect(self.screen, self.text_color, self.restart_button, 2)  # Border
        
        restart_text = self.font_small.render("Restart (R)", True, self.text_color)
        restart_text_rect = restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Draw quit button
        quit_color = self.button_hover_color if self.quit_hovered else self.button_color
        pygame.draw.rect(self.screen, quit_color, self.quit_button)
        pygame.draw.rect(self.screen, self.text_color, self.quit_button, 2)  # Border
        
        quit_text = self.font_small.render("Quit (Q)", True, self.text_color)
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)
        
        # Draw instructions
        instruction_text = self.font_small.render("Press R to restart or ESC to quit", True, self.text_color)
        instruction_rect = instruction_text.get_rect(center=(self.center_x, self.screen.get_height() - 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def _draw_leaderboard(self) -> None:
        """Draw the top 5 leaderboard only if game was completed"""
        if not self.game_completed:
            # Show message about completing the game to enter leaderboard
            message_text = self.font_small.render("Complete todos os mapas para entrar no ranking!", True, (255, 255, 0))
            message_rect = message_text.get_rect(center=(self.center_x, 200))
            self.screen.blit(message_text, message_rect)
            return

        # Title
        leaderboard_title = self.font_medium.render("TOP 5 MELHORES TEMPOS", True, (255, 215, 0))  # Gold
        title_rect = leaderboard_title.get_rect(center=(self.center_x, 180))
        self.screen.blit(leaderboard_title, title_rect)

        # Get top scores
        top_scores = self.leaderboard.get_top_scores(5)

        if not top_scores:
            no_scores_text = self.font_small.render("Nenhum recorde ainda!", True, self.text_color)
            no_scores_rect = no_scores_text.get_rect(center=(self.center_x, 220))
            self.screen.blit(no_scores_text, no_scores_rect)
            return

        # Draw scores
        start_y = 220
        for i, entry in enumerate(top_scores):
            rank = i + 1
            color = self._get_rank_color(rank)

            # Format: "1. PlayerName - 02:45"
            score_text = f"{rank}. {entry.name} - {entry.get_time_formatted()}"

            score_surface = self.font_small.render(score_text, True, color)
            score_rect = score_surface.get_rect(center=(self.center_x, start_y + (i * 30)))
            self.screen.blit(score_surface, score_rect)
    
    def _get_rank_color(self, rank: int) -> tuple:
        """Get color for rank position"""
        if rank == 1:
            return (255, 215, 0)    # Gold
        elif rank == 2:
            return (192, 192, 192)  # Silver
        elif rank == 3:
            return (205, 127, 50)   # Bronze
        else:
            return (255, 255, 255)  # White
