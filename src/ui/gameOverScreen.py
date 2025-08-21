"""
Game Over Screen - Displayed when player dies
"""
import pygame
from typing import Callable
from src.core.enums import GameState

class GameOverScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
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
        
        # Draw "GAME OVER" title
        game_over_text = self.font_large.render("GAME OVER", True, self.red_accent)
        game_over_rect = game_over_text.get_rect(center=(self.center_x, self.center_y - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw subtitle
        subtitle_text = self.font_medium.render("You were eliminated!", True, self.text_color)
        subtitle_rect = subtitle_text.get_rect(center=(self.center_x, self.center_y - 50))
        self.screen.blit(subtitle_text, subtitle_rect)
        
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
        instruction_rect = instruction_text.get_rect(center=(self.center_x, self.center_y + 200))
        self.screen.blit(instruction_text, instruction_rect)
