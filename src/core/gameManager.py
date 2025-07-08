import pygame
import sys
from enum import Enum, auto
from src.world.core.gameWorld import GameWorld


WIDTH: int = 960
HEIGHT: int = 960
TARGET_FPS: int = 60

class GameState(Enum):
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    MENU = auto()

class GameManager:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT, fps: int = TARGET_FPS) -> None:
        pygame.init()
        self.width: int = width
        self.height: int = height
        self.screen: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Linha Direta - The Game")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.target_fps: int = fps
        
        self.state: GameState = GameState.RUNNING
        
        self.game_world: GameWorld = GameWorld(self.screen, self.clock, self.width, self.height)

    def toggle_pause(self) -> None:
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING

    def handle_events(self) -> None:
        self._process_system_events()
        
        self._process_keyboard_input()

    def _process_keyboard_input(self) -> None:
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.RUNNING:
            self.game_world.process_player_input(keys)
            mouse_pos = pygame.mouse.get_pos()
            self.game_world.process_player_mouse_movement(mouse_pos)
        
        if keys[pygame.K_ESCAPE]:
            self.state = GameState.GAME_OVER
    
    def _process_system_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = GameState.GAME_OVER
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == GameState.RUNNING:
                mouse_pos = pygame.mouse.get_pos()
                self.game_world.process_player_mouse(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.toggle_pause()

    def _draw_pause_overlay(self) -> None:
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        
        self.screen.blit(overlay, (0, 0))
        
        try:
            font = pygame.font.Font("assets/fonts/techno_hideo.ttf", 64)
        except:
            font = pygame.font.Font(None, 64)
            
        pause_text = font.render("PAUSADO", True, (255, 255, 255))
        
        text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
        
        self.screen.blit(pause_text, text_rect)

    def run(self) -> None:
        try:
            while self.state != GameState.GAME_OVER:
                delta_time: float = self.clock.tick(self.target_fps) / 1000.0
                
                self.handle_events()
                
                if self.state == GameState.RUNNING:
                    self.game_world.update(delta_time)
                
                self.game_world.render()
                
                if self.state == GameState.PAUSED:
                    self._draw_pause_overlay()
                
                pygame.display.flip()
        except Exception as e:
            print(f"Erro no jogo: {e}")
        finally:
            pygame.quit()
            sys.exit()