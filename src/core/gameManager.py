import pygame
import sys
from enum import Enum, auto
from src.world.core.gameWorld import GameWorld
from src.core.audioManager import AudioManager 
from src.ui.hud import Hud


WIDTH: int = 950
HEIGHT: int = 800
TARGET_FPS: int = 60

class GameState(Enum):
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    MENU = auto()

class GameManager:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT, fps: int = TARGET_FPS) -> None:
        pygame.init()
        
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.width: int = width
        self.height: int = height
        self.screen: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Linha Direta - The Game")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.target_fps: int = fps
        
        self.state: GameState = GameState.RUNNING
        
        self.game_world: GameWorld = GameWorld(self.screen, self.clock, self.width, self.height)
        
        self.audio_manager = AudioManager()
        
        self.footstep_timer = 0
        
        self.audio_manager.play_background_music()
        self.hud = Hud(self.screen, self.game_world.player, self.clock)
        
        self.timer_running = True
        self.timer_start = pygame.time.get_ticks()
        self.timer_paused_at = 0
        self.elapsed_time = 0
        

    def toggle_pause(self) -> None:
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
            self.timer_runnig = False
            self.timer_paused_at = pygame.time.get_ticks()
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            self.timer_runnig = True
            pause_duration = pygame.time.get_ticks() - self.timer_paused_at
            self.timer_start += pause_duration

    def handle_events(self) -> None:
        self._process_system_events()
        
        self._process_keyboard_input()

    def _process_keyboard_input(self) -> None:
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.RUNNING:
            self.game_world.process_player_input(keys)
            mouse_pos = pygame.mouse.get_pos()
            self.game_world.process_player_mouse_movement(mouse_pos)
            
            if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
                self.footstep_timer += 1
                if self.footstep_timer >= 20:
                    self.audio_manager.play_sound('footstep')
                    self.footstep_timer = 0
            else:
                self.footstep_timer = 0
        
        if keys[pygame.K_KP_PLUS]: 
            current_vol = self.audio_manager.music_volume
            self.audio_manager.set_music_volume(current_vol + 0.01)
        
        if keys[pygame.K_KP_MINUS]: 
            current_vol = self.audio_manager.music_volume
            self.audio_manager.set_music_volume(current_vol - 0.01)
        
        if keys[pygame.K_ESCAPE]:
            self.state = GameState.GAME_OVER
        
        if keys[pygame.K_1]:  # Tecla 1 - ativa suavização rápida
            self.set_camera_smoothing(True, 0.5)
        
        if keys[pygame.K_2]:  # Tecla 2 - ativa suavização lenta
            self.set_camera_smoothing(True, 0.1)
        
        if keys[pygame.K_3]:  # Tecla 3 - desativa suavização
            self.set_camera_smoothing(False)
        
        if keys[pygame.K_F1]:  # F1 - mostra informações de debug
            self._show_debug_info = not getattr(self, '_show_debug_info', False)

    def _process_system_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = GameState.GAME_OVER
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == GameState.RUNNING:
                mouse_pos = pygame.mouse.get_pos()
                self.game_world.process_player_mouse(mouse_pos)
                
                self.audio_manager.play_sound('shoot')
                
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

    def set_camera_smoothing(self, enabled: bool, factor: float = 0.1) -> None:
        if hasattr(self.game_world, 'camera'):
            self.game_world.camera.set_smoothing(enabled, factor)
    
    def get_camera_position(self) -> tuple:
        if hasattr(self.game_world, 'camera'):
            return (self.game_world.camera.x, self.game_world.camera.y)
        return (0, 0)
    
    def get_player_position(self) -> tuple:
        if self.game_world.player:
            return self.game_world.player.position
        return (0, 0)

    def run(self) -> None:
        try:
            while self.state != GameState.GAME_OVER:
                delta_time: float = self.clock.tick(self.target_fps) / 1000.0
                
                self.handle_events()
                
                if self.timer_running:
                    self.elapsed_time = pygame.time.get_ticks() - self.timer_start
                
                if self.state == GameState.RUNNING:
                    self.game_world.update(delta_time)

                self.game_world.render()

                if self.state == GameState.RUNNING:
                    self.hud.player = self.game_world.player
                    self.hud.draw(elapsed_time=self.elapsed_time)
                
                if self.state == GameState.PAUSED:
                    self._draw_pause_overlay()
                
                self.hud.draw_debug_info(self) 
                
                pygame.display.flip()
        except Exception as e:
            print(f"Erro no jogo: {e}")
        finally:
            pygame.quit()
            sys.exit()