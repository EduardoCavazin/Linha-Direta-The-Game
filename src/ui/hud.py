import pygame
from typing import Any
from src.core.constants import Rendering

class Hud:
    def __init__(self, screen: pygame.Surface, player: Any, clock: pygame.time.Clock) -> None:
        self.screen: pygame.Surface = screen
        self.player: Any = player
        self.clock: pygame.time.Clock = clock
        self.font: pygame.font.Font = pygame.font.Font(None, 36)

    def draw(self, elapsed_time=None) -> None:
        health_text: pygame.Surface = self.font.render(
            f"Health: {self.player.health}", True, (255, 255, 255)
        )
        self.screen.blit(health_text, Rendering.HEALTH_POS)

        ammo_text: pygame.Surface = self.font.render(
            f"Ammo: {self.player.ammo}", True, (255, 255, 255)
        )
        self.screen.blit(ammo_text, Rendering.AMMO_POS)

        fps: int = int(self.clock.get_fps())
        fps_text: pygame.Surface = self.font.render(
            f"FPS: {fps}", True, (255, 255, 255)
        )
        x = self.screen.get_width() - fps_text.get_width() - 10
        y = 10
        self.screen.blit(fps_text, (x, y))
        
        if elapsed_time is not None:
            seconds = elapsed_time // 1000
            millis = elapsed_time % 1000
            timer_text = self.font.render(f" {seconds}:{millis:03d}", True, (255, 255, 255))
            self.screen.blit(timer_text, Rendering.TIMER_POS)
        

    def draw_debug_info(self, game_manager) -> None:
        if not getattr(game_manager, '_show_debug_info', False):
            return

        try:
            font = pygame.font.Font(None, 24)
        except:
            return

        camera_pos = game_manager.get_camera_position()
        player_pos = game_manager.get_player_position()
        mouse_screen_pos = pygame.mouse.get_pos()
        mouse_world_pos = (0, 0)
        if hasattr(game_manager.game_world, 'camera'):
            mouse_world_pos = game_manager.game_world.camera.screen_to_world(mouse_screen_pos)

        debug_lines = [
            f"Camera: ({camera_pos[0]:.0f}, {camera_pos[1]:.0f})",
            f"Player: ({player_pos[0]:.0f}, {player_pos[1]:.0f})",
            f"Mouse (Screen): ({mouse_screen_pos[0]}, {mouse_screen_pos[1]})",
            f"Mouse (World): ({mouse_world_pos[0]:.0f}, {mouse_world_pos[1]:.0f})",
            f"Bullets: {len(game_manager.game_world.bullets)}",
            f"FPS: {game_manager.clock.get_fps():.0f}",
            "Controls:",
            "1/2/3 - Camera smoothing",
            "F1 - Toggle debug info"
        ]

        y_offset = 10
        for line in debug_lines:
            text = font.render(line, True, (255, 255, 255))
            bg_rect = pygame.Rect(10, y_offset, text.get_width() + 10, text.get_height())
            pygame.draw.rect(self.screen, Rendering.TRANSPARENT_BLACK, bg_rect)
            self.screen.blit(text, (15, y_offset))
            y_offset += 25
