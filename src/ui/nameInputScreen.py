"""
Name Input Screen - Tela para o jogador inserir seu nome no leaderboard
"""
import pygame
from typing import Optional

class NameInputScreen:
    def __init__(self, screen: pygame.Surface, game_time: int):
        self.screen = screen
        self.game_time = game_time
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Colors
        self.background_color = (20, 30, 40)  # Dark blue
        self.text_color = (255, 255, 255)     # White
        self.input_color = (60, 80, 100)      # Dark input background
        self.input_active_color = (80, 120, 160)  # Active input
        self.green_accent = (50, 200, 50)     # Green for success
        
        # Input state
        self.player_name = ""
        self.max_name_length = 20
        self.input_active = True
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # ms
        
        # Screen dimensions
        self.center_x = screen.get_width() // 2
        self.center_y = screen.get_height() // 2
        
        # Input box
        self.input_box = pygame.Rect(
            self.center_x - 200,
            self.center_y,
            400,
            60
        )
        
        # Buttons
        self.submit_button = pygame.Rect(
            self.center_x - 100,
            self.center_y + 100,
            200,
            50
        )
        
        # State
        self.submitted = False
        self.submit_hovered = False
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events, returns action or None"""
        if event.type == pygame.KEYDOWN:
            if self.input_active and not self.submitted:
                if event.key == pygame.K_RETURN:
                    if self.player_name.strip():
                        self.submitted = True
                        return "submit"
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return "skip"
                else:
                    # Add character if within limit and is printable
                    if len(self.player_name) < self.max_name_length:
                        char = event.unicode
                        if char.isprintable() and char not in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                            self.player_name += char
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.submit_button.collidepoint(event.pos) and self.player_name.strip():
                self.submitted = True
                return "submit"
            # Click on input box to activate
            elif self.input_box.collidepoint(event.pos):
                self.input_active = True
        
        elif event.type == pygame.MOUSEMOTION:
            self.submit_hovered = self.submit_button.collidepoint(event.pos)
        
        return None
    
    def update(self, delta_time: int) -> None:
        """Update cursor blinking"""
        self.cursor_timer += delta_time
        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def get_time_formatted(self) -> str:
        """Format game time as mm:ss"""
        seconds = self.game_time // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def draw(self) -> None:
        """Draw the name input screen"""
        # Background
        self.screen.fill(self.background_color)
        
        # Title
        title_text = self.font_large.render("Novo Recorde!", True, self.green_accent)
        title_rect = title_text.get_rect(center=(self.center_x, self.center_y - 150))
        self.screen.blit(title_text, title_rect)
        
        # Time display
        time_text = f"Seu Tempo: {self.get_time_formatted()}"
        time_surface = self.font_medium.render(time_text, True, self.text_color)
        time_rect = time_surface.get_rect(center=(self.center_x, self.center_y - 100))
        self.screen.blit(time_surface, time_rect)
        
        # Input label
        label_text = self.font_small.render("Digite seu nome:", True, self.text_color)
        label_rect = label_text.get_rect(center=(self.center_x, self.center_y - 40))
        self.screen.blit(label_text, label_rect)
        
        # Input box
        input_color = self.input_active_color if self.input_active else self.input_color
        pygame.draw.rect(self.screen, input_color, self.input_box)
        pygame.draw.rect(self.screen, self.text_color, self.input_box, 2)
        
        # Input text
        display_text = self.player_name
        if self.input_active and self.cursor_visible and not self.submitted:
            display_text += "|"
        
        if display_text:
            input_surface = self.font_medium.render(display_text, True, self.text_color)
            # Center text in input box
            text_rect = input_surface.get_rect(center=self.input_box.center)
            self.screen.blit(input_surface, text_rect)
        
        # Submit button (only if name is entered)
        if self.player_name.strip():
            button_color = (80, 120, 80) if self.submit_hovered else (60, 100, 60)
            pygame.draw.rect(self.screen, button_color, self.submit_button)
            pygame.draw.rect(self.screen, self.text_color, self.submit_button, 2)
            
            submit_text = self.font_small.render("Salvar", True, self.text_color)
            submit_rect = submit_text.get_rect(center=self.submit_button.center)
            self.screen.blit(submit_text, submit_rect)
        
        # Instructions
        if not self.submitted:
            instructions = [
                "Enter - Salvar nome",
                "ESC - Pular",
                f"Máximo {self.max_name_length} caracteres"
            ]
            
            y_offset = self.center_y + 180
            for instruction in instructions:
                inst_surface = self.font_small.render(instruction, True, (180, 180, 180))
                inst_rect = inst_surface.get_rect(center=(self.center_x, y_offset))
                self.screen.blit(inst_surface, inst_rect)
                y_offset += 30
    
    def get_name(self) -> str:
        """Get the entered player name"""
        return self.player_name.strip() or "Anônimo"