import pygame
import sys
from src.world.core.gameWorld import GameWorld
from src.core.audioManager import AudioManager 
from src.ui.hud import Hud
from src.ui.gameOverScreen import GameOverScreen
from src.ui.nameInputScreen import NameInputScreen
from src.core.enums import GameState
from src.core.utils import create_overlay
from src.core.constants import Rendering
from src.core.leaderboard import Leaderboard


WIDTH: int = 950
HEIGHT: int = 800
TARGET_FPS: int = 60

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
        
        self.state: GameState = GameState.PLAYING
        
        self.audio_manager = AudioManager()
        
        self.game_world: GameWorld = GameWorld(self.screen, self.clock, self.width, self.height, self.audio_manager)
        
        self.footstep_timer = 0
        
        self.audio_manager.play_background_music()
        self.leaderboard = Leaderboard()
        self.hud = Hud(self.screen, self.game_world.player, self.clock)
        self.game_over_screen = None  # Will be created when needed
        self.name_input_screen = None  # Will be created when needed
        
        self.timer_running = True
        self.timer_start = pygame.time.get_ticks()
        self.timer_paused_at = 0
        self.elapsed_time = 0
        

    def toggle_pause(self) -> None:
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            self.timer_running = False
            self.timer_paused_at = pygame.time.get_ticks()
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            self.timer_running = True
            pause_duration = pygame.time.get_ticks() - self.timer_paused_at
            self.timer_start += pause_duration

    def handle_events(self) -> None:
        self._process_system_events()
        
        self._process_keyboard_input()

    def _process_keyboard_input(self) -> None:
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.PLAYING:
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
        
        
        # Game Over controls
        if self.state == GameState.GAME_OVER:
            if keys[pygame.K_r]:
                self._restart_game()
            elif keys[pygame.K_q]:
                self.state = GameState.QUIT  # Will exit main loop
        
        # Playing state controls
        elif self.state == GameState.PLAYING:
            if keys[pygame.K_1]:  # Tecla 1 - ativa suavização rápida
                self.set_camera_smoothing(True, 0.5)
            
            if keys[pygame.K_2]:  # Tecla 2 - ativa suavização lenta
                self.set_camera_smoothing(True, 0.1)
            
            if keys[pygame.K_3]:  # Tecla 3 - desativa suavização
                self.set_camera_smoothing(False)
            
            if keys[pygame.K_F1]:  # F1 - mostra informações de debug
                self._show_debug_info = not getattr(self, '_show_debug_info', False)
            
            if keys[pygame.K_F2]:  # F2 - mostra informações detalhadas de hitbox
                self._show_detailed_debug = not getattr(self, '_show_detailed_debug', False)

    def _process_system_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = GameState.QUIT
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == GameState.PLAYING:
                    mouse_pos = pygame.mouse.get_pos()
                    shot_successful = self.game_world.process_player_mouse(mouse_pos)
                    if shot_successful:
                        self.audio_manager.play_sound('shoot')
                    else:
                        self.audio_manager.play_sound('dryfire')
                    
                elif self.state == GameState.GAME_OVER and self.game_over_screen:
                    mouse_pos = pygame.mouse.get_pos()
                    action = self.game_over_screen.handle_click(mouse_pos)
                    if action == "restart":
                        self._restart_game()
                    elif action == "quit":
                        self.state = GameState.QUIT
                
                elif self.state == GameState.NAME_INPUT and self.name_input_screen:
                    action = self.name_input_screen.handle_event(event)
                    if action == "submit":
                        self._save_score_and_continue()
                    elif action == "skip":
                        # Player completed the game but skipped name input
                        self.game_over_screen = GameOverScreen(self.screen, game_completed=True)
                        self.game_over_screen.leaderboard = self.leaderboard
                        self.state = GameState.GAME_OVER
                        
            elif event.type == pygame.MOUSEMOTION:
                if self.state == GameState.GAME_OVER and self.game_over_screen:
                    self.game_over_screen.handle_mouse_motion(event.pos)
                elif self.state == GameState.NAME_INPUT and self.name_input_screen:
                    self.name_input_screen.handle_event(event)
                
            elif event.type == pygame.KEYDOWN:
                # ESC para pausar/despausar
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.toggle_pause()
                    elif self.state == GameState.PAUSED:
                        self.toggle_pause()
                    elif self.state == GameState.GAME_OVER:
                        pass  # Não fazer nada no game over
                
                # P também pode pausar (alternativa)
                elif event.key == pygame.K_p and self.state in [GameState.PLAYING, GameState.PAUSED]:
                    self.toggle_pause()
                
                # R para resetar quando pausado
                elif event.key == pygame.K_r and self.state == GameState.PAUSED:
                    self._restart_game()
                
                # X para sair do jogo quando pausado
                elif event.key == pygame.K_x and self.state == GameState.PAUSED:
                    self.state = GameState.QUIT
                
                # Controles do name input
                elif self.state == GameState.NAME_INPUT and self.name_input_screen:
                    action = self.name_input_screen.handle_event(event)
                    if action == "submit":
                        self._save_score_and_continue()
                    elif action == "skip":
                        # Player completed the game but skipped name input
                        self.game_over_screen = GameOverScreen(self.screen, game_completed=True)
                        self.game_over_screen.leaderboard = self.leaderboard
                        self.state = GameState.GAME_OVER
                
                # Controles do game over
                elif self.state == GameState.GAME_OVER and self.game_over_screen:
                    action = self.game_over_screen.handle_keypress(event.key)
                    if action == "restart":
                        self._restart_game()
                    elif action == "quit":
                        self.state = GameState.QUIT

    def _draw_pause_overlay(self) -> None:
        overlay = create_overlay((self.width, self.height), Rendering.OVERLAY_COLOR)
        
        self.screen.blit(overlay, (0, 0))
        
        try:
            font_large = pygame.font.Font("assets/fonts/techno_hideo.ttf", Rendering.PAUSE_FONT_SIZE)
            font_small = pygame.font.Font("assets/fonts/techno_hideo.ttf", Rendering.PAUSE_FONT_SIZE // 2)
        except:
            font_large = pygame.font.Font(None, Rendering.PAUSE_FONT_SIZE)
            font_small = pygame.font.Font(None, Rendering.PAUSE_FONT_SIZE // 2)
            
        # Título "PAUSADO"
        pause_text = font_large.render("PAUSADO", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        # Instruções de controle
        controls = [
            "ESC ou P - Continuar",
            "R - Resetar Jogo",
            "X - Sair do Jogo"
        ]
        
        y_offset = self.height // 2 + 10
        for control in controls:
            control_text = font_small.render(control, True, (200, 200, 200))
            control_rect = control_text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(control_text, control_rect)
            y_offset += 35

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
            while self.state != GameState.QUIT:
                delta_time: float = self.clock.tick(self.target_fps) / 1000.0
                
                self.handle_events()
                
                if self.timer_running:
                    self.elapsed_time = pygame.time.get_ticks() - self.timer_start
                
                if self.state == GameState.PLAYING:
                    self.game_world.update(delta_time)
                    
                    # Check if player died
                    if self.game_world.player and not self.game_world.player.is_alive():
                        self._handle_player_death()
                        self.audio_manager.stop_background_music()
                    
                    # Check if game was completed
                    elif self.game_world.is_game_completed():
                        self._handle_game_completion()
                        self.audio_manager.stop_background_music()

                self.game_world.render()
                
                # Renderizar hitboxes de debug se habilitado
                show_debug = getattr(self, '_show_debug_info', False)
                show_detailed = getattr(self, '_show_detailed_debug', False)
                if show_debug:
                    self.game_world.render_debug_hitboxes(True, show_detailed)

                if self.state == GameState.PLAYING:
                    self.hud.player = self.game_world.player
                    self.hud.draw(elapsed_time=self.elapsed_time)
                
                elif self.state == GameState.GAME_OVER and self.game_over_screen:
                    self.game_over_screen.draw()
                
                elif self.state == GameState.NAME_INPUT:
                    if self.name_input_screen:
                        self.name_input_screen.update(delta_time)
                        self.name_input_screen.draw()
                
                elif self.state == GameState.PAUSED:
                    self._draw_pause_overlay()
                
                self.hud.draw_debug_info(self) 
                
                pygame.display.flip()
        except Exception as e:
            pass
        finally:
            pygame.quit()
            sys.exit()
    
    def _restart_game(self) -> None:
        """Restart the game by creating new game world"""
        self.state = GameState.PLAYING
        self.game_world = GameWorld(self.screen, self.clock, self.width, self.height, self.audio_manager)
        self.hud = Hud(self.screen, self.game_world.player, self.clock)
        self.audio_manager.play_background_music()

        # Clear screens
        self.game_over_screen = None
        self.name_input_screen = None

        # Reset timer
        self.timer_running = True
        self.timer_start = pygame.time.get_ticks()
        self.timer_paused_at = 0
    
    def _handle_player_death(self) -> None:
        """Handle player death - go directly to game over (no leaderboard entry)"""
        # Player died before completing the game, go directly to game over
        self.game_over_screen = GameOverScreen(self.screen, game_completed=False)
        self.game_over_screen.leaderboard = self.leaderboard
        self.state = GameState.GAME_OVER
    
    def _handle_game_completion(self) -> None:
        """Handle game completion - player finished all maps successfully"""
        current_time = self.elapsed_time

        # Check if this time would make it to top 10
        if self.leaderboard.is_top_score(current_time, 10):
            # Show name input screen
            self.name_input_screen = NameInputScreen(self.screen, current_time)
            self.state = GameState.NAME_INPUT
        else:
            # Go directly to game over with completion flag
            self.game_over_screen = GameOverScreen(self.screen, game_completed=True)
            self.game_over_screen.leaderboard = self.leaderboard
            self.state = GameState.GAME_OVER
    
    def _save_score_and_continue(self) -> None:
        """Save the player's score and continue to game over screen"""
        if self.name_input_screen:
            player_name = self.name_input_screen.get_name()
            current_time = self.elapsed_time

            # Save to leaderboard
            position = self.leaderboard.add_score(player_name, current_time)


            # Go to game over screen with completion flag
            self.game_over_screen = GameOverScreen(self.screen, game_completed=True)
            self.game_over_screen.leaderboard = self.leaderboard
            self.state = GameState.GAME_OVER
            self.name_input_screen = None
    
    def _format_time(self, time_ms: int) -> str:
        """Format time in milliseconds to mm:ss format"""
        seconds = time_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"